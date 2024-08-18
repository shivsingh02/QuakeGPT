echo "Building app..."
npm run build

echo "Deploying files to server..."
scp -r build/* gpt@10.29.8.94:/var/www/10.29.8.88/

echo "Done!"