<?php
header('Content-Type: application/json');

require "../configPHP/aes.php";
require "../configPHP/config.php";

$aes = new AesEncryption($key);
$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die(json_encode(['error' => '数据库连接失败: ' . $conn->connect_error]));
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => '仅允许 POST 请求']);
    $conn->close();
    exit;
}

$json = file_get_contents('php://input');
$data = json_decode($json, true);

$email = $data['email'] ?? null;
$password = $data['password'] ?? null;
$need_auto_login = $data['auto_login'] ?? null;
$session = $data['session'] ?? null;

if (!$session && (!isset($email) || !isset($password))) {
    http_response_code(400);
    echo json_encode(['error' => 'Email 和 Password 是必需的']);
    $conn->close();
    exit;
}

$stmt = $conn->prepare("SELECT id, email, password, sessions FROM accounts WHERE " . ($session ? "sessions = ?" : "email = ?"));
$param = $session ? $session : $email;
$stmt->bind_param("s", $param);
$stmt->execute();
$result = $stmt->get_result();
$row = $result->fetch_assoc();

if (!$row) {
    http_response_code(401);
    echo json_encode(['error' => '邮箱或密码错误！']);
    $stmt->close();
    $conn->close();
    exit;
}

$valid = false;
$userId = $row['id'];
$userEmail = $row['email'];
$userPassword = $row['password'];

if (!$session) {
    $valid = ($password === $userPassword);
} else {
    $decrypted = json_decode($aes->decrypt($session), true);
    $valid = ($decrypted && $decrypted['email'] === $userEmail && $decrypted['password'] === $userPassword);
}

if (!$valid) {
    http_response_code(401);
    echo json_encode(['error' => '邮箱或密码错误！']);
    $stmt->close();
    $conn->close();
    exit;
}

$encrypted_session = "";
if ($need_auto_login) {
    $session_data = json_encode([
        'email' => $userEmail,
        'password' => $userPassword,
        'user_id' => $userId,
        'time' => time(),
    ]);
    $encrypted_session = $aes->encrypt($session_data);
    $update_stmt = $conn->prepare("UPDATE accounts SET sessions = ? WHERE id = ?");
    $update_stmt->bind_param("si", $encrypted_session, $userId);
    $update_stmt->execute();
    $update_stmt->close();
}

$role = $userEmail === "2953911716@qq.com" ? "dev" : "user";
http_response_code(200);
echo json_encode([
    'success' => '登录成功',
    'user_id' => $userId,
    'role' => $role,
    'session' => $encrypted_session,
    'create_time' => $row['time'] ?? null
]);

$stmt->close();
$conn->close();