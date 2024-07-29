<?php
$users_file = 'users.txt';
$username = htmlspecialchars($_POST['username']);
$password = htmlspecialchars($_POST['password']);
$email = htmlspecialchars($_POST['email']);

file_put_contents($users_file, "$username,$password,$email\n", FILE_APPEND);

// Redirect to the Streamlit chatbot page
header('Location: http://localhost:8501');
exit;
?>
