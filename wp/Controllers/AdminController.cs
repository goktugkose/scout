using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using System.Linq;
using wp_user_stories.Models;

namespace wp_user_stories.Controllers
{
    [AllowAnonymous]
    public class AdminController : Controller
    {
        public ActionResult Index()
        {
            return View();
        }

        public ActionResult addProject()
        {
            return View();
        }

        [HttpPost]
        public ActionResult addProject(Project p)
        {
            UserStory db = new UserStory();
            db.projects.Add(new Project() { projectName = p.projectName });
            db.SaveChanges();
            return RedirectToAction("Index");
        }

        public ActionResult addTeam()
        {
            return View();
        }

        [HttpPost]
        public ActionResult addTeam(Team t)
        {
            UserStory db = new UserStory();
            db.teams.Add(new Team() { teamName = t.teamName });
            db.SaveChanges();
            return RedirectToAction("Index");
        }

        public ActionResult addUser()
        {
            UserStory db = new UserStory();
            ViewBag.teams = new SelectList(db.teams.Select(x => new { x.teamID, x.teamName }).ToList(), "teamID", "teamName");
            return View();
        }

        [HttpPost]
        public ActionResult addUser(string userName, int teamID)
        {
            UserStory db = new UserStory();
            db.users.Add(new User() { userName = userName, team = db.teams.Where(x => x.teamID == teamID).FirstOrDefault() });
            db.SaveChanges();
            return RedirectToAction("Index");
        }

        public ActionResult addUserProject()
        {
            UserStory db = new UserStory();
            ViewBag.userList = new SelectList(db.users.Select(x => new { x.userID, x.userName }).ToList(), "userID", "userName");
            ViewBag.projectList = new SelectList(db.projects.Select(x => new { x.ProjectID, x.projectName }).ToList(), "ProjectID", "projectName");
            ViewBag.scenarioList = new SelectList(db.scenarios.Select(x => new { x.scenarioGroup }).ToList(), "scenarioGroup", "scenarioGroup");
            return View();

        }

        [HttpPost]
        public ActionResult addUserProject(int userId, int projectId, int scenarioGroup)
        {
            UserStory db = new UserStory();
            db.userProject.Add(new UserProject() { projectID = projectId, scenarioGroup = scenarioGroup, userID = userId });
            db.SaveChanges();
            return RedirectToAction("Index");
        }
    }
}