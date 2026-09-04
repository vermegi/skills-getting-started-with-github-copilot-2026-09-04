using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Mvc.Testing;

namespace tests;

public class ActivitiesApiTests(WebApplicationFactory<Program> factory) : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient client = factory.CreateClient(new WebApplicationFactoryClientOptions
    {
        AllowAutoRedirect = false
    });

    [Fact]
    public async Task Root_redirects_to_static_index()
    {
        var response = await client.GetAsync("/");

        Assert.Equal(HttpStatusCode.TemporaryRedirect, response.StatusCode);
        Assert.Equal("/static/index.html", response.Headers.Location?.OriginalString);
    }

    [Fact]
    public async Task Get_activities_returns_seeded_activities()
    {
        var activities = await client.GetFromJsonAsync<Dictionary<string, Activity>>("/activities");

        Assert.NotNull(activities);
        Assert.Equal(9, activities.Count);
        Assert.Equal("Fridays, 3:30 PM - 5:00 PM", activities["Chess Club"].Schedule);
        Assert.Equal(["michael@mergington.edu", "daniel@mergington.edu"], activities["Chess Club"].Participants);
    }

    [Fact]
    public async Task Signup_adds_student_to_activity()
    {
        var response = await client.PostAsync("/activities/Soccer%20Club/signup?email=alex%40mergington.edu", null);

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal("{\"message\":\"Signed up alex@mergington.edu for Soccer Club\"}", await response.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task Duplicate_signup_returns_bad_request()
    {
        var response = await client.PostAsync("/activities/Chess%20Club/signup?email=michael%40mergington.edu", null);

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        Assert.Equal("{\"detail\":\"Student already signed up for this activity\"}", await response.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task Unregister_removes_student_from_activity()
    {
        var response = await client.DeleteAsync("/activities/Programming%20Class/participants?email=emma%40mergington.edu");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal("{\"message\":\"Unregistered emma@mergington.edu from Programming Class\"}", await response.Content.ReadAsStringAsync());
    }

    [Fact]
    public async Task Unregister_student_not_signed_up_returns_not_found()
    {
        var response = await client.DeleteAsync("/activities/Basketball%20Team/participants?email=alex%40mergington.edu");

        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
        Assert.Equal("{\"detail\":\"Student is not signed up for this activity\"}", await response.Content.ReadAsStringAsync());
    }
}
