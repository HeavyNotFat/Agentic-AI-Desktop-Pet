<?php
header('Content-Type: application/json');
require "../configPHP/config.php";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die(json_encode(["error" => "Connection failed: " . $conn->connect_error]));
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    die(json_encode(["error" => "请求方法不正确"]));
}

$json = file_get_contents('php://input');
$data = json_decode($json, true);
$email = $data['email'] ?? '';
$code = $data['code'] ?? '';
$password = $data['password'] ?? '';
$time = date('Y-m-d H:i:s');

if (empty($email) || empty($code) || empty($password)) {
    die(json_encode(["error" => "缺少必需的参数"]));
}

$sql = "SELECT * FROM register_data WHERE address = ?";
$stmt = $conn->prepare($sql);
$stmt->bind_param("s", $email);
$stmt->execute();
$result = $stmt->get_result();
$row = $result->fetch_assoc();

if ($row) {
    $outdate = $row['outdate'];
    $vertify = $row['vertify'];
    $fail_times = $row['fail_times'];

    if (strtotime($outdate) < strtotime($time)) {
        die(json_encode(["error" => "验证码已过期"]));
    }

    if ($vertify === $code) {
        $insertSql = "INSERT INTO accounts (email, password, time) VALUES (?, ?, ?)";
        $insertStmt = $conn->prepare($insertSql);
        $insertStmt->bind_param("sss", $email, $password, $time);
        $insertStmt->execute();

        $deleteSql = "DELETE FROM register_data WHERE address = ?";
        $deleteStmt = $conn->prepare($deleteSql);
        $deleteStmt->bind_param("s", $email);
        $deleteStmt->execute();

        die(json_encode(["success" => "验证成功！感谢您的注册！！！"]));
    } else {
        $fail_times++;
        if ($fail_times > 5) {
            $deleteSql = "DELETE FROM register_data WHERE address = ?";
            $deleteStmt = $conn->prepare($deleteSql);
            $deleteStmt->bind_param("s", $email);
            $deleteStmt->execute();
            die(json_encode(["error" => "验证失败次数过多。账户已禁用"]));
        } else {
            $updateSql = "UPDATE register_data SET fail_times = ? WHERE address = ?";
            $updateStmt = $conn->prepare($updateSql);
            $updateStmt->bind_param("is", $fail_times, $email);
            $updateStmt->execute();
            die(json_encode(["error" => "验证码不正确！"]));
        }
    }
} else {
    die(json_encode(["error" => "邮箱未找到，您可能已经注册了！"]));
}

$conn->close();
?>
