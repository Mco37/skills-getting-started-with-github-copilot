document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Create participants section
        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";
        
        if (details.participants.length > 0) {
          const participantsTitle = document.createElement("strong");
          participantsTitle.textContent = "Registered Participants:";
          participantsSection.appendChild(participantsTitle);
          
          const participantsList = document.createElement("ul");
          participantsList.className = "participants-list";
          
          details.participants.forEach(p => {
            const listItem = document.createElement("li");
            listItem.style.listStyle = "none";
            listItem.style.display = "flex";
            listItem.style.alignItems = "center";
            
            const emailSpan = document.createElement("span");
            emailSpan.textContent = p;
            listItem.appendChild(emailSpan);
            
            const deleteButton = document.createElement("button");
            deleteButton.className = "delete-participant";
            deleteButton.setAttribute("aria-label", `Remove ${p} from ${name}`);
            deleteButton.setAttribute("data-activity", name);
            deleteButton.setAttribute("data-email", p);
            deleteButton.textContent = "🗑️";
            deleteButton.addEventListener("click", handleDeleteParticipant);
            
            listItem.appendChild(deleteButton);
            participantsList.appendChild(listItem);
          });
          
          participantsSection.appendChild(participantsList);
        } else {
          participantsSection.className = "participants-section empty";
          const emptyMessage = document.createElement("em");
          emptyMessage.textContent = "No participants registered yet.";
          participantsSection.appendChild(emptyMessage);
        }

        // Create activity card content
        const titleElement = document.createElement("h4");
        titleElement.textContent = name;
        
        const descElement = document.createElement("p");
        descElement.textContent = details.description;
        
        const scheduleElement = document.createElement("p");
        const scheduleLabel = document.createElement("strong");
        scheduleLabel.textContent = "Schedule: ";
        scheduleElement.appendChild(scheduleLabel);
        scheduleElement.appendChild(document.createTextNode(details.schedule));
        
        const availabilityElement = document.createElement("p");
        const availabilityLabel = document.createElement("strong");
        availabilityLabel.textContent = "Availability: ";
        availabilityElement.appendChild(availabilityLabel);
        availabilityElement.appendChild(document.createTextNode(`${spotsLeft} spots left`));

        activityCard.appendChild(titleElement);
        activityCard.appendChild(descElement);
        activityCard.appendChild(scheduleElement);
        activityCard.appendChild(availabilityElement);
        activityCard.appendChild(participantsSection);

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

  // Handle delete participant
  async function handleDeleteParticipant(e) {
    const button = e.currentTarget;
    const activityName = button.getAttribute('data-activity');
    const email = button.getAttribute('data-email');
    
    if (confirm(`Remove ${email} from ${activityName}?`)) {
      try {
        const response = await fetch(`/activities/${encodeURIComponent(activityName)}/unregister`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email: email })
        });
        const result = await response.json();
        if (response.ok) {
          fetchActivities();
        } else {
          alert(result.detail || 'Error removing participant');
        }
      } catch (err) {
        alert('Network error while removing participant');
      }
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup`,
        {
          method: "POST",
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ email: email })
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // Refresh list after signup
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
  fetchActivities();
});
