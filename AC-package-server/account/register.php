<?php

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

require 'vendor/autoload.php';
require "../configPHP/config.php";

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) die("连接失败: " . $conn->connect_error);

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => '仅允许 POST 请求']);
    $conn->close();
    exit;
}

$data = json_decode(file_get_contents('php://input'), true);
$to = $data['to'] ?? null;

if (!$to) {
    http_response_code(400);
    echo json_encode(['error' => '邮件地址是必需的']);
    $conn->close();
    exit;
}

$outdate = date('Y-m-d H:i:s', strtotime('+30 minutes'));
$ip = $_SERVER['REMOTE_ADDR'];
$address = $to;

$stmt = $conn->prepare("SELECT id, outdate, sent_times FROM register_data WHERE address = ?");
$stmt->bind_param("s", $address);
$stmt->execute();
$result = $stmt->get_result();
$row = $result->fetch_assoc();
$stmt->close();

$id = null;
$sent_times = 0;

if ($row) {
    $id = $row['id'];
    $sent_times = (int)$row['sent_times'];

    if ($sent_times >= 5 && strtotime($row['outdate']) > time()) {
        http_response_code(429);
        echo json_encode(['error' => '触发流控限制: 5P/30min']);
        $conn->close();
        exit;
    }

    $sent_times++;
    $stmt = $conn->prepare("UPDATE register_data SET outdate = ?, sent_times = ? WHERE id = ?");
    $stmt->bind_param("sii", $outdate, $sent_times, $id);
    $stmt->execute();
    $stmt->close();
} else {
    $sent_times = 1;
    $stmt = $conn->prepare("INSERT INTO register_data (outdate, address, ip, sent_times) VALUES (?, ?, ?, ?)");
    $stmt->bind_param("sssi", $outdate, $address, $ip, $sent_times);
    $stmt->execute();
    $id = $stmt->insert_id;
    $stmt->close();
}

$vertify = strtoupper(substr(str_shuffle("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"), 0, 6));

$stmt = $conn->prepare("UPDATE register_data SET vertify = ? WHERE id = ?");
$stmt->bind_param("si", $vertify, $id);
$stmt->execute();
$stmt->close();

$mail = new PHPMailer(true);

try {
    $mail->isSMTP();
    $mail->Host       = '';
    $mail->SMTPAuth   = true;
    $mail->Username   = '';
    $mail->Password   = '';
    $mail->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
    $mail->Port       = 80;
    $mail->setFrom('', 'AI Desktop Pet');
    $mail->addAddress($to);
    $mail->isHTML(true);
    $mail->Subject = 'Ai Desktop Pet 注册';
    $mail->Body = "
    <!DOCTYPE html>
    <html lang=\"zh-CN\">
    <head>
        <meta charset=\"UTF-8\">
        <style>
            body { font-family: Arial, sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); width: 400px; text-align: center; }
            h1 { font-size: 24px; margin-bottom: 20px; }
            p { font-size: 18px; color: #333; }
            .verification-code { font-size: 24px; font-weight: bold; color: #e74c3c; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class=\"container\">
            <h1>感谢您的注册</h1>
            <p>您的验证码为：<span class=\"verification-code\">$vertify</span></p>
        </div>
    </body>
    </html>";

    $mail->send();
    echo json_encode(['success' => '邮件已发送']);
} catch (Exception $e) {
    echo json_encode(['error' => "邮件发送失败: {$mail->ErrorInfo}"]);
}

$conn->close();
?>