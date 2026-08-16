<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    http_response_code(200);
    $response = ["version" => "3.16.2"];
    echo json_encode($response);
} else {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
}
?>
