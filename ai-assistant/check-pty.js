const { spawn } = require('child_process');
const os = require('os');

console.log('Checking PTY alternatives for Windows...\n');

// Check system info
console.log('System Info:');
console.log('- Platform:', os.platform());
console.log('- Node version:', process.version);
console.log('- Architecture:', os.arch());
console.log('');

// Test 1: Check if we can spawn PowerShell
console.log('Testing PowerShell spawn...');
try {
  const ps = spawn('powershell.exe', ['-NoProfile', '-Command', 'echo "Hello from PowerShell"']);
  
  ps.stdout.on('data', (data) => {
    console.log('✓ PowerShell output:', data.toString().trim());
  });
  
  ps.on('exit', (code) => {
    console.log('PowerShell exited with code:', code);
  });
} catch (error) {
  console.error('✗ PowerShell spawn failed:', error.message);
}

// Test 2: Check if we can spawn CMD
console.log('\nTesting CMD spawn...');
try {
  const cmd = spawn('cmd.exe', ['/c', 'echo Hello from CMD']);
  
  cmd.stdout.on('data', (data) => {
    console.log('✓ CMD output:', data.toString().trim());
  });
  
  cmd.on('exit', (code) => {
    console.log('CMD exited with code:', code);
  });
} catch (error) {
  console.error('✗ CMD spawn failed:', error.message);
}

// Test 3: Check Windows Terminal availability
console.log('\nChecking Windows Terminal...');
const wt = spawn('where', ['wt']);
wt.stdout.on('data', (data) => {
  console.log('✓ Windows Terminal found at:', data.toString().trim());
});
wt.stderr.on('data', (data) => {
  console.log('✗ Windows Terminal not found');
});

// Suggest alternatives
setTimeout(() => {
  console.log('\n=== PTY Alternatives for Windows ===');
  console.log('1. Use child_process.spawn() with shell: true for basic terminal');
  console.log('2. Install Windows Build Tools: npm install --global windows-build-tools');
  console.log('3. Use Visual Studio Installer to add Spectre-mitigated libs');
  console.log('4. Try node-pty-prebuilt: npm install node-pty-prebuilt');
  console.log('5. Use WebSocket-based terminal server as fallback');
}, 1000);