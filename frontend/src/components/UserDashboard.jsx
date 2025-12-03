// src/components/UserDashboard.jsx
import React, { useState, useEffect, useContext } from "react";
import { AuthContext } from "../contexts/AuthContext";
import "./UserDashboard.css";

const API_BASE = "http://192.168.0.75:8020";

export default function UserDashboard() {
  const { token, logout } = useContext(AuthContext);

  const [storageUsed, setStorageUsed] = useState(0);
  const [numImages, setNumImages] = useState(0);

  const [uploadFile, setUploadFile] = useState(null);
  const [zipFile, setZipFile] = useState(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);

  // ---------------------------------------------------
  // Fetch user's own stats using /user/me (NEW ENDPOINT)
  // ---------------------------------------------------
  const fetchUserStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        console.error("Failed to fetch /user/me");
        return;
      }

      const data = await res.json();

      setStorageUsed(data.storage_bytes);
      setNumImages(data.num_images);
    } catch (err) {
      console.error("Fetch user stats failed:", err);
    }
  };

  useEffect(() => {
    if (token) fetchUserStats();
  }, [token]);

  // ---------------------------------------------------
  // Upload single image
  // ---------------------------------------------------
  const handleUpload = async () => {
    if (!uploadFile) return alert("Select a file first");

    const formData = new FormData();
    formData.append("file", uploadFile);

    try {
      const res = await fetch(`${API_BASE}/upload/`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        return alert("Upload failed: " + err.detail);
      }

      alert("Image queued successfully!");

      await fetchUserStats(); // refresh

      setUploadFile(null);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }
  };

  // ---------------------------------------------------
  // Upload ZIP file
  // ---------------------------------------------------
  const handleZipUpload = async () => {
    if (!zipFile) return alert("Select a ZIP file first");

    const formData = new FormData();
    formData.append("file", zipFile);

    try {
      const res = await fetch(`${API_BASE}/upload/zip`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        return alert("ZIP upload failed: " + data.detail);
      }

      alert(`Queued ${data.total_queued} images from ZIP`);

      await fetchUserStats(); // refresh

      setZipFile(null);
    } catch (err) {
      console.error(err);
      alert("ZIP upload failed");
    }
  };

  // ---------------------------------------------------
  // Search
  // ---------------------------------------------------
  const handleSearch = async () => {
    if (!searchQuery) return;

    try {
      const res = await fetch(
        `${API_BASE}/search/?query=${encodeURIComponent(searchQuery)}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (!res.ok) {
        const err = await res.json();
        return alert("Search failed: " + err.detail);
      }

      setSearchResults(await res.json());
    } catch (err) {
      console.error(err);
      alert("Search failed");
    }
  };

  return (
  <div className="dashboard-container">
    <h2 className="dashboard-title">User Dashboard</h2>

    <div className="stats-box">
      <p>
        <strong>Storage used:</strong>{" "}
        {(storageUsed / 1_000_000).toFixed(2)} MB / 1000 MB
      </p>
      <p>
        <strong>Images uploaded:</strong> {numImages}
      </p>
    </div>

    <div className="section">
      <h3>Upload Image</h3>
      <input
        type="file"
        className="file-input"
        onChange={(e) => setUploadFile(e.target.files[0])}
      />
      <button className="btn" onClick={handleUpload}>
        Upload
      </button>
    </div>

    <div className="section">
      <h3>Upload ZIP</h3>
      <input
        type="file"
        className="file-input"
        onChange={(e) => setZipFile(e.target.files[0])}
      />
      <button className="btn" onClick={handleZipUpload}>
        Upload ZIP
      </button>
    </div>

    <div className="section">
      <h3>Search Images</h3>
      <input
        type="text"
        className="search-input"
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
      />
      <button className="btn" onClick={handleSearch}>
        Search
      </button>

      <div className="results-grid">
        {searchResults.map((img) => (
          <div className="result-card" key={img.id}>
            <img
              src={`${API_BASE}${img.filepath}`}
              alt={img.filename}
              className="result-image"
            />
            <p className="result-name">{img.filename}</p>
          </div>
        ))}
      </div>
    </div>

    <button className="logout-btn" onClick={logout}>
      Logout
    </button>
  </div>
);
}
