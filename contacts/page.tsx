"use client";

import { useState } from "react";

export default function ContactsPage() {
  const [db, setDb] = useState("070");
  const [query, setQuery] = useState("");
  const [contacts, setContacts] = useState([]);
  const [message, setMessage] = useState("");

  const fetchContacts = async () => {
    setMessage("Loading...");
    try {
      const url = `http://127.0.0.1:8000/contacts/search/?db=${db}&q=${query}`;
      const res = await fetch(url);
      
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      
      const data = await res.json();
      setContacts(data.results || []);
      
      if (data.results.length === 0) {
        setMessage(`No contacts found in database ${db}`);
      } else {
        setMessage(`Found ${data.results.length} contacts in ${db}`);
      }
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    }
  };

  return (
    <div style={{
      padding: "100px 20px 20px",  // push down below header
      minHeight: "100vh",
      backgroundColor: "#f5f5f5"  // light background
    }}>
      <div style={{
        maxWidth: 800,
        margin: "0 auto",
        background: "white",
        padding: 30,
        borderRadius: 8,
        boxShadow: "0 2px 10px rgba(0,0,0,0.1)"
      }}>
        <h1 style={{ marginBottom: 20, color: "#333" }}>Contact Search</h1>
        
        <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
          <select 
            value={db} 
            onChange={(e) => setDb(e.target.value)}
            style={{ padding: "10px 15px", fontSize: 16 }}
          >
            <option value="070">070</option>
            <option value="080">080</option>
            <option value="090">090</option>
            <option value="081">081</option>
          </select>

          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search..."
            style={{ 
              flex: 1, 
              padding: "10px 15px", 
              fontSize: 16,
              border: "1px solid #ddd",
              borderRadius: 4
            }}
          />
          
          <button 
            onClick={fetchContacts}
            style={{
              padding: "10px 25px",
              fontSize: 16,
              background: "#007bff",
              color: "white",
              border: "none",
              borderRadius: 4,
              cursor: "pointer"
            }}
          >
            Search
          </button>
        </div>

        <p style={{ 
          color: message.includes("Error") ? "red" : message.includes("No") ? "orange" : "green",
          fontWeight: "bold"
        }}>
          {message}
        </p>

        <ul style={{ 
          listStyle: "none", 
          padding: 0,
          maxHeight: 500,
          overflowY: "auto"
        }}>
          {contacts.map((contact, index) => (
            <li key={index} style={{
              padding: "12px 15px",
              borderBottom: "1px solid #eee",
              fontSize: 18,
              fontFamily: "monospace"
            }}>
              📞 {contact.phone}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}