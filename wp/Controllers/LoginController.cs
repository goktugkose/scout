using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Threading.Tasks;
using wp_user_stories.Models;
using wp_user_stories.Views.Login.ViewModels;

namespace wp_user_stories.Controllers
{
    [AllowAnonymous]
    public class LoginController : Controller
    {
        // GET: Login
        public ActionResult Index()
        {
            UserStory db = new UserStory();
            ViewBag.projects = new SelectList(db.projects.Select(x => new { x.ProjectID, x.projectName }).OrderBy(x => x.projectName).ToList(),
                "ProjectID", "projectName");
            ViewBag.users = new SelectList(db.users.Select(x => new { x.userID, x.userName }).OrderBy(x => x.userName).ToList(),
                "userID", "userName");
            return View();
        }

        [HttpPost]
        public async Task <IActionResult> Index(UserInfo u)
        {
            UserStory db = new UserStory();
            UserProject up = db.userProject.Where(x => x.projectID.ToString() == u.project && x.userID.ToString() == u.user).FirstOrDefault();
            if (up != null)
            {
                var claims = new List<Claim>
                {
                new Claim(ClaimTypes.Name, u.user)
                    };
                var userIdentity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
                ClaimsPrincipal principal = new ClaimsPrincipal(userIdentity);
                await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, principal, new AuthenticationProperties()
                {
                    IsPersistent = true
                });

                HttpContext.Session.setObject("user",u);
                return RedirectToAction("Index", "Home");
            }
            else
            {
                TempData["loginError"] = "You are not authorized to see this project!";
                return RedirectToAction("Index");
            }

        }

        public ActionResult Logout()
        {
            HttpContext.SignOutAsync();
            return RedirectToAction("Index");
        }
    }
}