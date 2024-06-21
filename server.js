const express = require('express');
const bodyParser = require('body-parser');
const { MongoClient } = require('mongodb');

const app = express();
const port = 3000;

// Middleware to parse JSON bodies
app.use(bodyParser.json());

// MongoDB connection URI
const uri = 'mongodb://localhost:27017'; // Change this to your MongoDB URI

// Database and collection names
const dbName = 'your_database_name';
const collectionName = 'students';

// MongoDB client
const client = new MongoClient(uri, { useNewUrlParser: true, useUnifiedTopology: true });

// Connect to MongoDB
client.connect().then(() => {
  console.log('Connected to MongoDB');
}).catch(err => console.error('Error connecting to MongoDB:', err));

// Handle student login
app.post('/login', async (req, res) => {
  const { username, password } = req.body;

  const collection = client.db(dbName).collection(collectionName);
  
  // Query MongoDB to find a student with matching username and password
  const student = await collection.findOne({ username, password });
  
  if (student) {
    res.json({ success: true, message: 'Login successful' });
  } else {
    res.status(401).json({ success: false, message: 'Invalid credentials' });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
