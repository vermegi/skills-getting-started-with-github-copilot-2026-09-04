var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

var activities = new Dictionary<string, Activity>(StringComparer.Ordinal)
{
	["Chess Club"] = new("Learn strategies and compete in chess tournaments", "Fridays, 3:30 PM - 5:00 PM", 12, ["michael@mergington.edu", "daniel@mergington.edu"]),
	["Programming Class"] = new("Learn programming fundamentals and build software projects", "Tuesdays and Thursdays, 3:30 PM - 4:30 PM", 20, ["emma@mergington.edu", "sophia@mergington.edu"]),
	["Gym Class"] = new("Physical education and sports activities", "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", 30, ["john@mergington.edu", "olivia@mergington.edu"]),
	["Basketball Team"] = new("Practice basketball skills and compete in school games", "Tuesdays and Thursdays, 4:00 PM - 5:30 PM", 15, []),
	["Soccer Club"] = new("Develop soccer skills and play friendly matches", "Wednesdays, 3:30 PM - 5:00 PM", 22, []),
	["Art Club"] = new("Explore drawing, painting, and other visual art techniques", "Mondays, 3:30 PM - 5:00 PM", 18, []),
	["Drama Club"] = new("Perform plays and build confidence through theater", "Thursdays, 3:30 PM - 5:00 PM", 20, []),
	["Debate Club"] = new("Build research, public speaking, and critical thinking skills", "Tuesdays, 3:30 PM - 4:30 PM", 16, []),
	["Science Club"] = new("Conduct experiments and explore fascinating scientific topics", "Fridays, 3:30 PM - 4:30 PM", 20, [])
};

app.UseStaticFiles();

app.MapGet("/", () => Results.Redirect("/static/index.html", permanent: false, preserveMethod: true));
app.MapGet("/activities", () => Results.Ok(activities));

app.MapPost("/activities/{activityName}/signup", (string activityName, string email) =>
{
	if (!activities.TryGetValue(activityName, out var activity))
	{
		return Results.NotFound(new { detail = "Activity not found" });
	}

	if (activity.Participants.Contains(email))
	{
		return Results.BadRequest(new { detail = "Student already signed up for this activity" });
	}

	activity.Participants.Add(email);
	return Results.Ok(new { message = $"Signed up {email} for {activityName}" });
});

app.MapDelete("/activities/{activityName}/participants", (string activityName, string email) =>
{
	if (!activities.TryGetValue(activityName, out var activity))
	{
		return Results.NotFound(new { detail = "Activity not found" });
	}

	if (!activity.Participants.Remove(email))
	{
		return Results.NotFound(new { detail = "Student is not signed up for this activity" });
	}

	return Results.Ok(new { message = $"Unregistered {email} from {activityName}" });
});

app.Run();

public sealed record Activity(string Description, string Schedule, int MaxParticipants, List<string> Participants);

public partial class Program;
