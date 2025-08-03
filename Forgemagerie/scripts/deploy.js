#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

console.log('🚀 Starting deployment process...');

try {
  // Change to backend directory
  const backendDir = path.join(__dirname, '..', 'backend');
  process.chdir(backendDir);
  
  console.log('📦 Installing backend dependencies...');
  execSync('npm install', { stdio: 'inherit' });
  
  console.log('🗄️ Generating Prisma client...');
  execSync('npx prisma generate', { stdio: 'inherit' });
  
  console.log('🗄️ Pushing database schema...');
  execSync('npx prisma db push', { stdio: 'inherit' });
  
  console.log('🏗️ Building backend...');
  execSync('npm run build', { stdio: 'inherit' });
  
  // Change to frontend directory
  const frontendDir = path.join(__dirname, '..', 'frontend');
  process.chdir(frontendDir);
  
  console.log('📦 Installing frontend dependencies...');
  execSync('npm install', { stdio: 'inherit' });
  
  console.log('🏗️ Building frontend...');
  execSync('npm run build', { stdio: 'inherit' });
  
  console.log('✅ Deployment process completed successfully!');
  
} catch (error) {
  console.error('❌ Deployment failed:', error.message);
  process.exit(1);
}