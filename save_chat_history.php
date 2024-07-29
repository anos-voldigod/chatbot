<?php
// Database connection parameters
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "chatbotdb";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// Get JSON data from POST request
$json_data = $_POST['chat_history'];
$chat_history = json_decode($json_data, true);

if ($chat_history) {
    // Prepare SQL statement
    $stmt = $conn->prepare("INSERT INTO chat_history (sender, message, tts_audio_link) VALUES (?, ?, ?)");
    $stmt->bind_param("sss", $sender, $message, $tts_audio_link);

    // Insert each entry into the database
    foreach ($chat_history as $entry) {
        $sender = $entry['sender'];
        $message = $entry['message'];
        $tts_audio_link = isset($entry['tts_audio_link']) ? $entry['tts_audio_link'] : NULL;
        
        $stmt->execute();
    }

    $stmt->close();
    echo "Chat history saved successfully!";
} else {
    echo "Invalid chat history data.";
}

$conn->close();
?>
