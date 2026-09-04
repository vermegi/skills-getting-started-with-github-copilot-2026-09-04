document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const analyticsList = document.getElementById("analytics-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function escapeHtml(value) {
    const element = document.createElement("div");
    element.textContent = value;
    return element.innerHTML;
  }

  async function fetchAnalytics() {
    try {
      const response = await fetch("/activities/analytics");
      const analytics = await response.json();

      analyticsList.innerHTML = "";
      Object.entries(analytics).forEach(([name, metrics]) => {
        const analyticsCard = document.createElement("div");
        analyticsCard.className = "analytics-card";
        analyticsCard.innerHTML = `
          <div class="analytics-header">
            <h4>${escapeHtml(name)}</h4>
            <span class="utilization-pill">${metrics.utilization_percentage}%</span>
          </div>
          <p><strong>Participants:</strong> ${metrics.total_participants}</p>
          <p><strong>Open seats:</strong> ${metrics.remaining_seats}</p>
        `;
        analyticsList.appendChild(analyticsCard);
      });
    } catch (error) {
      analyticsList.innerHTML = "<p>Failed to load analytics.</p>";
      console.error("Error fetching analytics:", error);
    }
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantItems = details.participants.length
          ? details.participants
              .map(
                (participant) => `
                  <li>
                    <span>${escapeHtml(participant)}</span>
                    <button
                      class="remove-participant"
                      type="button"
                      data-activity="${escapeHtml(name)}"
                      data-email="${escapeHtml(participant)}"
                      aria-label="Unregister ${escapeHtml(participant)} from ${escapeHtml(name)}"
                      title="Unregister participant"
                    >&times;</button>
                  </li>`
              )
              .join("")
          : '<li class="no-participants">No participants yet</li>';

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <strong>Participants</strong>
            <ul class="participants-list">${participantItems}</ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  activitiesList.addEventListener("click", async (event) => {
    const removeButton = event.target.closest(".remove-participant");
    if (!removeButton) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(removeButton.dataset.activity)}/participants?email=${encodeURIComponent(removeButton.dataset.email)}`,
        { method: "DELETE" }
      );
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Unable to unregister participant");
      }

      messageDiv.textContent = result.message;
      messageDiv.className = "success";
      messageDiv.classList.remove("hidden");
      await fetchActivities();
    } catch (error) {
      messageDiv.textContent = error.message || "Unable to unregister participant";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering participant:", error);
    }
  });

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchAnalytics();
  fetchActivities();
});
