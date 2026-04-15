const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// 🔍 DEBUG LOG
console.log("Trying to connect to MongoDB...");

// 🔗 CONNECT TO MONGODB
mongoose.connect("mongodb+srv://cotonourow:changeMOD123@cluster0.omcdjre.mongodb.net/myDatabase?retryWrites=true&w=majority")
.then(() => console.log("MongoDB connected ✅"))
.catch(err => console.log("MongoDB ERROR ❌:", err));

// Test route
app.get("/", (req, res) => {
  res.send("API is working 🚀");
});

// Start server
app.listen(5000, () => {
  console.log("Server running on port 5000");
});