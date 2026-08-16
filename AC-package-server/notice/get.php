<?php
// 文件路径
$file_path = 'board';

// 获取请求方法
$request_method = $_SERVER["REQUEST_METHOD"];

switch ($request_method) {
    case 'GET':
        get_lines();
        break;
    case 'POST':
        post_lines();
        break;
    default:
        header("HTTP/1.0 405 Method Not Allowed");
        break;
}

function get_lines() {
    global $file_path;
    if (file_exists($file_path)) {
        $lines = file($file_path, FILE_IGNORE_NEW_LINES);
        echo json_encode($lines, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE);
    } else {
        header("HTTP/1.0 404 Not Found");
        echo json_encode(["error" => "文件不存在"]);
    }
}

function post_lines() {
    global $file_path;
    $data = json_decode(file_get_contents("php://input"), true);

    if (!isset($data['lines']) || !is_array($data['lines'])) {
        header("HTTP/1.0 400 Bad Request");
        echo json_encode(["error" => "请求数据格式不正确"]);
        return;
    }

    $lines = $data['lines'];

    try {
        file_put_contents($file_path, implode("\n", $lines));
        echo json_encode(["message" => "文件写入成功"]);
    } catch (Exception $e) {
        header("HTTP/1.0 500 Internal Server Error");
        echo json_encode(["error" => $e->getMessage()]);
    }
}
?>
