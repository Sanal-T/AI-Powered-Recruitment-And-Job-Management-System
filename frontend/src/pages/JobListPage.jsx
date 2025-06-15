import React, { useEffect, useState } from "react";

const JobListPage = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/jobs?region=Delhi")
      .then(res => res.json())
      .then(data => {
        setJobs(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching jobs:", err);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Jobs in Delhi</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        jobs.map((job) => (
          <div
            key={job.url}
            style={{
              border: "1px solid #ccc",
              borderRadius: "8px",
              padding: "1rem",
              marginBottom: "1rem",
            }}
          >
            <h2>{job.title}</h2>
            <p><strong>{job.company}</strong> – {job.region}</p>
            <p>Source: <em>{job.source}</em></p>
            <a href={job.url} target="_blank" rel="noopener noreferrer">
              Apply Now
            </a>
          </div>
        ))
      )}
    </div>
  );
};

export default JobListPage;
