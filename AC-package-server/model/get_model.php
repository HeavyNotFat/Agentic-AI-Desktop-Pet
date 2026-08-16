<?php

header("Content-Type: application/json");

// 允许跨域请求（CORS）
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: GET, POST");
setlocale(LC_ALL, 'zh_CN.GBK');

// 获取请求方法
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET' || $method === 'POST') {

    // 获取当前目录
    $dir = __DIR__;

    // 压缩文件扩展名白名单
    $validExtensions = ['zip', 'tar', 'gz', 'rar'];

    // 存储压缩文件列表
    $archiveFiles = [];
    $archiveUrl = [];
    $archiveIcons = [];
    $archiveDescriptions = [];

    if (is_dir($dir)) {
        $files = scandir($dir);

        foreach ($files as $file) {
            if ($file === '.' || $file === '..') continue;

            $filePath = $dir . DIRECTORY_SEPARATOR . $file;
            if (!is_file($filePath)) continue;

            $ext = strtolower(pathinfo($file, PATHINFO_EXTENSION));

            if (in_array($ext, $validExtensions)) {
                $archiveFiles[] = $file;
                $archiveUrl[] = "https://adp.nekocode.top/model/$file";
                $archiveIcons[] = "https://adp.nekocode.top/model/" . basename($file, ".zip") . ".png";

                // 查找同名的.txt文件并读取内容
                $descriptionFile = pathinfo($file, PATHINFO_FILENAME) . '.txt';
                $descriptionFilePath = $dir . DIRECTORY_SEPARATOR . $descriptionFile;
                if (file_exists($descriptionFilePath)) {
                    $archiveDescriptions[] = file_get_contents($descriptionFilePath);
                } else {
                    $archiveDescriptions[] = ""; // 如果没有找到对应的.txt文件，则设置为空字符串
                }
            }
        }

        echo json_encode([
            "status" => "success",
            "archives" => $archiveFiles,
            "urls" => $archiveUrl,
            "icons" => $archiveIcons,
            "descriptions" => $archiveDescriptions,
        ], JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);

    } else {
        http_response_code(500);
        echo json_encode([
            "status" => "error",
            "message" => "无法访问当前目录"
        ]);
    }

} else {
    http_response_code(405);
    echo json_encode([
        "status" => "error",
        "message" => "不支持的请求方法"
    ]);
}
