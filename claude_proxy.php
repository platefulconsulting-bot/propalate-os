<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => ['message' => 'Method not allowed']]);
    exit;
}

$ANTHROPIC_KEY = getenv('ANTHROPIC_API_KEY') ?: '';
if (!$ANTHROPIC_KEY && file_exists(__DIR__ . '/config.local.php')) {
    $config = require __DIR__ . '/config.local.php';
    $ANTHROPIC_KEY = $config['anthropic_key'] ?? '';
}
if (!$ANTHROPIC_KEY) {
    http_response_code(500);
    echo json_encode(['error' => ['message' => 'API key not configured']]);
    exit;
}

$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data) {
    http_response_code(400);
    echo json_encode(['error' => ['message' => 'Invalid JSON input']]);
    exit;
}

$ch = curl_init('https://api.anthropic.com/v1/messages');
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST => true,
    CURLOPT_HTTPHEADER => [
        'Content-Type: application/json',
        'x-api-key: ' . $ANTHROPIC_KEY,
        'anthropic-version: 2023-06-01'
    ],
    CURLOPT_POSTFIELDS => $input,
    CURLOPT_TIMEOUT => 120
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

if ($error) {
    http_response_code(502);
    echo json_encode(['error' => ['message' => 'Proxy error: ' . $error]]);
    exit;
}

http_response_code($httpCode);
echo $response;
