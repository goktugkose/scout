using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using wp_user_stories.Models;
namespace wp_user_stories
{
    public class DbInitializer
    {
        private readonly ModelBuilder modelBuilder;
        public DbInitializer(ModelBuilder modelBuilder)
        {
            this.modelBuilder = modelBuilder;
        }

        public void Seed()
        {
            int teamCount = 12;
            int personCount = 24;
            int scenarioCount = 2;

            List<Scenario> scenarios = new List<Scenario>()
            {
                new Scenario()
                {
                    scenarioID = 1,
                    scenarioGroup = 1,
                    scenarioLink = "<h4><b>Restaurant Management System</b></h4><p>A restaurant management system is a software designed to manage a restaurant’s primary operations. Restaurants use restaurant management systems to keep track of customer orders and store orders for different calculations such as total sales. These systems help restaurants with inventory management by keeping track of products and resources available. Additionally, menu items are organized through these systems depending on the stored inventory information. Employee data including clock in and out information is stored in such systems and should be available for editing. Managers can perform the same tasks as other employees, including editing items and employee information and generating reports.</p>"
                },
                 new Scenario()
                {
                    scenarioID = 2,
                    scenarioGroup = 2,
                    scenarioLink = "<h4><b>Library Management System</b></h4><p>A library management system is a software designed to manage a library's primary operations. Libraries use library management systems to keep track of their asset collections and interactions with their patrons. Library management systems assist libraries in keeping track of books and their checkouts, as well as subscriber profiles and subscriptions. Keeping track of new books and documenting books that have been borrowed with their due dates and user information is another part of library management systems along with calculating fines for delayed returns. Members of the library can look up books by title, author, subject category, and publication date or place reservations for books that are currently unavailable. Each book is assigned a unique identification number as well as additional information such as a shelf number, which aids identify the actual location of the book.</p>"
                }
            };

            List<Team> teams = new List<Team>() /*{ new Team() { teamID = 1, teamName = "Team-0" } }*/;
            List<User> users = new List<User>() /*{ new User() { userID = 1, teamID = teams[0].teamID, userName = "goktug.kose" }, new User() { userID = 2, teamID = teams[0].teamID, userName = "basak.aydemir" } }*/;
            List<Project> projects = new List<Project>() /*{ new Project() { ProjectID = 1, projectName = "Project-0" } }*/;
            List<UserProject> userProjects = new List<UserProject>() /*{ new UserProject() { userProjectID = 1, userID = users[0].userID, projectID = projects[0].ProjectID, scenarioGroup = scenarios[0].scenarioGroup }, new UserProject() { userProjectID = 2, userID = users[1].userID, projectID = projects[0].ProjectID, scenarioGroup = scenarios[0].scenarioGroup } }*/;

            /*for (int i = 0; i < personCount; i++)
            {
                projects.Add(new Project() { ProjectID = projects.Count()+1, projectName = "Project-P-" + (i + 1) });
            }*/

            for (int i = 0; i < teamCount; i++)
            {
                projects.Add(new Project() { ProjectID = projects.Count() + 1, projectName = "Project-" + (i + 1) });
            }

            int ctr = 1;
            for (int i = 0; i < teamCount; i++)
            {
                string teamName = "Team-" + (i + 1);
                Team t = new Team() { teamID = i+1, teamName = teamName };
                teams.Add(t);

                for (int y = 0; y < personCount / teamCount; y++)
                {
                    int idx = ctr;
                    string userName = "User-" + idx.ToString();
                    Team tmp = teams.Where(x => x.teamName == teamName).FirstOrDefault();
                    User u = new User() { userID = users.Count() + 1, teamID = tmp.teamID, userName = userName };
                    users.Add(u);

                    /*string pName = "Project-P-" + idx;
                    Project prj = projects.Where(x => x.projectName == pName).FirstOrDefault();
                    userProjects.Add(new UserProject() { userProjectID = userProjects.Count()+3, userID = u.userID, projectID = prj.ProjectID, scenarioGroup = idx % scenarioCount + 1 });
                    */

                    string pName = "Project-" + (i + 1);
                    Project prj = projects.Where(x => x.projectName == pName).FirstOrDefault();
                    int sg = idx > (personCount/scenarioCount) ? 1 : 2;
                    userProjects.Add(new UserProject() { userProjectID = userProjects.Count() + 1, userID = u.userID, projectID = prj.ProjectID, scenarioGroup = sg});
                    ctr++;
                }

            }

            List<SuggestionDetail> details = new List<SuggestionDetail>(){
                new SuggestionDetail()
            {
                suggestionName = "Isolated Concepts",
                mainSuggestionGroup = "Quality Suggestions",
                suggestionExp = "Concepts that are not related to other concepts.",
                suggestionHint = "You can add more user stories about them or remove user stories about these concepts.",
                suggestionGroup = "isolated",
                sugesstionType = "list",
                suggestionScope = 0,
            },
            new SuggestionDetail()
            {
                suggestionName = "Non-Atomic User Stories",
                mainSuggestionGroup = "Quality Suggestions",
                suggestionExp = "Atomicity must be provided when user stories are constructed.",
                suggestionGroup = "atomic",
                sugesstionType = "list",
                suggestionScope = 0,
                suggestionHint = "These user stories can be divided into more user stories."
            },
            new SuggestionDetail()
            {
                suggestionName = "CRUD Operation Issues",
                mainSuggestionGroup = "Quality Suggestions",
                suggestionExp = "These concepts miss the highlighted CRUD operations.",
                suggestionGroup = "crud",
                sugesstionType = "list",
                suggestionScope = 0,
                suggestionHint = "You can add user stories mentioning the missing operations."
            },
             new SuggestionDetail()
            {
                suggestionName = "You might add concepts to increase completeness.",
                mainSuggestionGroup = "Completeness Suggestions",
                suggestionExp = "You might add concepts to increase completeness.",
                suggestionGroup = "incomplete",
                sugesstionType = "dict",
                suggestionScope = 1,
                suggestionHint = "You might add concepts to increase completeness."
            },
            new SuggestionDetail()
            {
                suggestionName = "Popular concepts that are less mentioned by you.",
                mainSuggestionGroup = "Completeness Suggestions",
                suggestionExp = "It seems that the other members of the project frequently mention these concepts.",
                suggestionGroup = "pop-zero",
                sugesstionType = "list",
                suggestionScope = 1,
                suggestionHint = "Perhaps you can add some user stories about these concepts as well."
            },
            new SuggestionDetail()
            {
                suggestionName = "Concepts that are not mentioned by you but are related to the most popular concepts of the project.",
                mainSuggestionGroup = "Completeness Suggestions",
                suggestionExp = "These concepts are related to the most popular concepts of the project.",
                suggestionGroup = "pop-one",
                sugesstionType = "dict",
                suggestionScope = 1,
                suggestionHint = "Perhaps you can add some user stories about these concepts as well."
            },
            new SuggestionDetail()
            {
                suggestionName = "Concepts that are only mentioned by you and are related to the most popular concepts of the project.",
                mainSuggestionGroup = "Completeness Suggestions",
                suggestionExp = "These concepts are related to the most popular concepts of the project but they are ignored by the other members of the project.",
                suggestionGroup = "pop-two",
                sugesstionType = "dict",
                suggestionScope = 1,
                suggestionHint = "Perhaps you can add more user stories about them or re-consider the user stories that include them."
            },
            new SuggestionDetail()
            {
                suggestionName = "Concepts that are related to your most used concepts constructed by other members of the project.",
                mainSuggestionGroup = "Completeness Suggestions",
                suggestionExp = "Other members added user stories about these concepts which are related to your most used concepts.",
                suggestionGroup = "pop-three",
                sugesstionType = "dict",
                suggestionScope = 1,
                suggestionHint = "Perhaps you can add user stories about them as well."
            },
            new SuggestionDetail()
            {
                suggestionName = "Feeling Lucky?",
                mainSuggestionGroup = "Completeness Suggestions",
                suggestionExp = "These concepts are not related to the other concepts of the project.",
                suggestionGroup = "lucky",
                sugesstionType = "list",
                suggestionScope = 1,
                suggestionHint = "Perhaps you can add more user stories about them."
            },
            new SuggestionDetail()
            {
                suggestionName = "All is well!",
                mainSuggestionGroup = "Completeness Suggestions",
                suggestionExp = "All of the user stories are provide a complete solution.",
                suggestionGroup = "complete",
                sugesstionType = "list",
                suggestionScope = 1,
                suggestionHint = "No further changes needed."
            }
            };   
            modelBuilder.Entity<SuggestionDetail>().HasData((IEnumerable<object>)details);
            modelBuilder.Entity<Scenario>().HasData((IEnumerable<object>)scenarios);
            modelBuilder.Entity<Project>().HasData((IEnumerable<object>)projects);
            modelBuilder.Entity<Team>().HasData((IEnumerable<object>)teams);
            modelBuilder.Entity<User>().HasData((IEnumerable<object>)users);
            modelBuilder.Entity<UserProject>().HasData((IEnumerable<object>)userProjects);
        }
    }
}
