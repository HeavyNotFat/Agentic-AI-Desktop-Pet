<?php
require "../configPHP/aes.php";
require "../configPHP/config.php";

$aes = new AesEncryption($key);
$conn = new mysqli($servername, $username, $password, $dbname);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['status' => false, 'msg' => '请求方法不被允许']);
    exit;
}
if ($conn->connect_error) {
    die(json_encode(['error' => '数据库连接失败: ' . $conn->connect_error]));
}

$json = file_get_contents('php://input');
$json = json_decode($json, true);

if (!isset($json['type']) || !isset($json['filename']) || !isset($json['fileb64']) || !isset($json['token'])) {
    echo json_encode(['status' => false, 'msg' => '缺少参数']);
    exit;
}

$token = $json['token'];
$type = $json['type'];
$uploadDir = $type === 'model' ? '../model/' : '../plugin/';
$filenames = is_array($json['filename']) ? $json['filename'] : [$json['filename']];
$fileb64s = is_array($json['fileb64']) ? $json['fileb64'] : [$json['fileb64']];
$decrypted = $aes->decrypt($token);
if (!$decrypted) {
    http_response_code(401);
    echo json_encode(['status' => false, 'msg' => '无效的鉴权token，你可能没有登录！']);
    exit;
}
$decryptData = json_decode($decrypted, true);
if (!$decryptData || !isset($decryptData['email'], $decryptData['password'])) {
    http_response_code(401);
    echo json_encode(['status' => false, 'msg' => 'token 数据格式错误']);
    exit;
}
$email = $decryptData['email'];
$stmt = $conn->prepare("SELECT id, email, password FROM accounts WHERE email = ?");
$stmt->bind_param("s", $email);
$stmt->execute();
$result = $stmt->get_result();
$row = $result->fetch_assoc();
if (!$row) {
    http_response_code(401);
    echo json_encode(['status' => false, 'msg' => '用户不存在']);
    exit;
}
if ($decryptData['password'] != $row['password']) {
    http_response_code(401);
    echo json_encode(['status' => false, 'msg' => '密码不匹配或 token 已失效']);
    exit;
}

if ($type !== 'model' && $type !== 'plugin') {
    echo json_encode(['status' => false, 'msg' => '无效类型']);
    exit;
}
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0755, true);
}
if (count($filenames) !== count($fileb64s)) {
    echo json_encode(['status' => false, 'msg' => '文件名和文件数据数量不匹配']);
    exit;
}

$allowedMimeTypes = ['image/png' => 'png', 'application/zip' => 'zip', 'text/plain' => 'txt'];
$uploadedFiles = [];
foreach ($filenames as $index => $filename) {
    $filename = basename($filename);
    $fileb64 = $fileb64s[$index];
    $fileData = base64_decode($fileb64, true);
    if ($fileData === false) {
        continue;
    }
    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $mimeType = $finfo->buffer($fileData);
    if (!isset($allowedMimeTypes[$mimeType])) {
        echo json_encode(['status' => false, 'msg' => '不支持的文件类型']);
        exit;
    }
    $extension = $allowedMimeTypes[$mimeType];
    if (pathinfo($filename, PATHINFO_EXTENSION) !== $extension) {
        $filename = pathinfo($filename, PATHINFO_FILENAME) . '.' . $extension;
    }
    $filePath = $uploadDir . $filename;
    $counter = 1;
    $originalFilename = $filename;
    while (file_exists($filePath)) {
        $filename = pathinfo($originalFilename, PATHINFO_FILENAME) . '_' . $counter . '.' . $extension;
        $filePath = $uploadDir . $filename;
        $counter++;
    }
    if (file_put_contents($filePath, $fileData)) {
        $uploadedFiles[] = $filename;
    }
}
echo json_encode(['status' => true, 'msg' => '上传成功', '已上传文件' => $uploadedFiles]);
?>