#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

console.log('🚀 Starting deployment process...');

// Function to run command with error handling
function runCommand(command, cwd = process.cwd()) {
  console.log(`Running: ${command} in ${cwd}`);
  try {
    execSync(command, { stdio: 'inherit', cwd });
  } catch (error) {
    console.error(`❌ Command failed: ${command}`);
    throw error;
  }
}

try {
  const rootDir = path.join(__dirname, '..');
  const backendDir = path.join(rootDir, 'backend');
  const frontendDir = path.join(rootDir, 'frontend');
  
  // Install root dependencies first
  console.log('📦 Installing root dependencies...');
  runCommand('npm install', rootDir);
  
  // Backend setup
  console.log('📦 Installing backend dependencies...');
  runCommand('npm install', backendDir);
  
  console.log('🗄️ Generating Prisma client...');
  runCommand('npx prisma generate', backendDir);
  
  console.log('🗄️ Pushing database schema...');
  runCommand('npx prisma db push', backendDir);
  
  console.log('🏗️ Building backend...');
  runCommand('npm run build', backendDir);
  
  // Frontend setup
  console.log('📦 Installing frontend dependencies...');
  runCommand('npm install', frontendDir);
  
  console.log('🏗️ Building frontend...');
  runCommand('npm run build', frontendDir);
  
  console.log('✅ Deployment process completed successfully!');
  
} catch (error) {
  console.error('❌ Deployment failed:', error.message);
  process.exit(1);
}