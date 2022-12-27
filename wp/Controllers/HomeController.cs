using System;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;
using System.Text;
using System.IO;
using CsvHelper;
using wp_user_stories.Views.Login.ViewModels;
using System.Net;
using System.Threading.Tasks;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc.Filters;
using wp_user_stories.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore;
using System.Net.Http;

namespace wp_user_stories.Controllers
{
    [Authorize]
    public class HomeController : Controller
    {
        public string getHost(){
            IConfigurationRoot configuration = new ConfigurationBuilder()
           .SetBasePath(Directory.GetCurrentDirectory())
           .AddJsonFile("appsettings.json")
           .Build();
            return configuration.GetValue<string>("ws-host");
        }
        public async Task<bool> callNounPhraseExtractionModule(string user_id, string project_id)
        {
            string host = getHost();
            var url = "http://"+host+"/noun_phrase_extraction?user_id=" + user_id + "&project_id=" + project_id;
            string s = "";

            using (var client = new HttpClient())
            {
                s = await client.GetStringAsync(url);
            }
            return true;
        }
        public override async Task OnActionExecutionAsync(ActionExecutingContext context, ActionExecutionDelegate next)
        {
            if (HttpContext.Session.Get("user") == null)
            {
                context.Result = new RedirectResult("/Login/Index");
            }
            else
            {
                await next();
            }
        }

        public void addActionToDB(int userId, int projectID, string type)
        {
            UserStory db = new UserStory();
            db.actions.Add(new Models.Action() { actionTime = DateTime.Now, type = type, userID = userId, projectID= projectID});
            db.SaveChanges();
        }

        public ActionResult Index(int id = 0)
        {
            UserInfo info = HttpContext.Session.GetObject<UserInfo>("user");
            UserStory db = new UserStory();
            UserProject up = db.userProject.FirstOrDefault(x => x.projectID.ToString() == info.project && x.userID.ToString() == info.user);

            if (up == null)
            {
                User u = db.users.Where(x => x.userID.ToString() == info.user).FirstOrDefault();
                Project p = db.projects.Where(x => x.ProjectID.ToString() == info.project).FirstOrDefault();
                up = new UserProject() { project = p, user = u };
                db.userProject.Add(up);
                db.SaveChanges();
            }

            ViewBag.userInfo = new UserInfo()
            {
                user = up.user.userName,
                project = up.project.projectName,
                scenarioGroup = up.scenarioGroup
            };

            if (id != 0)
            {
                ViewBag.flag = false;
                ViewBag.story = db.stories.Where(x => x.storyID == id).FirstOrDefault();
            }
            else
            {
                ViewBag.flag = true;
            }
            List<Story> stories = db.stories.Where(x => x.projectID.ToString() == info.project && x.userID.ToString() == info.user && !x.isDeleted).ToList();
            List<SuggestionDetail> details = db.suggestionDetails.ToList();
            return View(new Tuple<List<Story>,List<SuggestionDetail>>(stories,details));

        }

        [HttpPost]
        public IActionResult addUserStory(string userStory)
        {
            UserInfo info = HttpContext.Session.GetObject<UserInfo>("user");
            UserStory db = new UserStory();
            var pattern = new Regex(@"(?i)^(as [a|an].*?)([,].*?)(i want to .*?)(?:(so that .*?))?$", RegexOptions.CultureInvariant);
            if (userStory.Contains("\n"))
            {
                List<string> us = userStory.Split('\n').ToList();
                bool flag = us.TrueForAll(x => pattern.IsMatch(x));
                if (flag)
                {
                    us.ForEach(x => db.stories.Add(new Story() { userStory = x.Trim('\r'), userID = Convert.ToInt32(info.user), projectID = Convert.ToInt32(info.project) }));
                }
                else
                {
                    TempData["importError"] = "There are sentences that are not in user story format!";
                }
            }
            else
            {
                if (pattern.IsMatch(userStory))
                {
                    db.stories.Add(new Story() { userStory = userStory, userID = Convert.ToInt32(info.user), projectID = Convert.ToInt32(info.project) });
                }
                else
                {
                    TempData["importError"] = "This sentence is not in user story format!";
                    TempData["wrongSentence"] = userStory;
                }
            }
            if (TempData["importError"] == null)
            {
                UserProject up = db.userProject.FirstOrDefault(x => x.userID.ToString() == info.user && x.projectID.ToString() == info.project);
                if (up == null)
                {
                    up = new UserProject() { userID = Convert.ToInt32(info.user), projectID = Convert.ToInt32(info.project), lastUserStorySaved = DateTime.Now };
                    db.Entry(up).State = EntityState.Added;
                }
                else
                {
                    up.lastUserStorySaved = DateTime.Now;
                    db.Entry(up).State = EntityState.Modified;
                }
                db.SaveChanges();

                addActionToDB(Convert.ToInt32(info.user), Convert.ToInt32(info.project), "add_user_story");

                //Task.Run(() => callNounPhraseExtractionModule(info.user, info.project));
            }
            return RedirectToAction("Index", "Home");
        }

        public IActionResult updateUserStory(int id)
        {
            UserStory db = new UserStory();
            return RedirectToAction("Index", "Home", new { @id = id });
        }

        [HttpPost]
        public IActionResult updateUserStory(Story s)
        {
            UserStory db = new UserStory();
            db.Entry(s).State = EntityState.Modified;

            UserInfo info = HttpContext.Session.GetObject<UserInfo>("user");
            UserProject up = db.userProject.FirstOrDefault(x => x.userID.ToString() == info.user && x.projectID.ToString() == info.project);
            up.lastUserStorySaved = DateTime.Now;
            db.Entry(up).State = EntityState.Modified;
            db.SaveChanges();

            addActionToDB(Convert.ToInt32(info.user), Convert.ToInt32(info.project), "update_user_story");

            //Task.Run(() => callNounPhraseExtractionModule(info.user, info.project));

            return RedirectToAction("Index", "Home", new { @id = 0 });
        }

        public IActionResult deleteUserStory(int id)
        {
            UserStory db = new UserStory();

            Story s = db.stories.Where(x => x.storyID == id).FirstOrDefault();
            s.isDeleted = true;
            db.Entry(s).State = EntityState.Modified;

            UserInfo info = HttpContext.Session.GetObject<UserInfo>("user");
            UserProject up = db.userProject.FirstOrDefault(x => x.userID.ToString() == info.user && x.projectID.ToString() == info.project);
            up.lastUserStorySaved = DateTime.Now;
            db.Entry(up).State = EntityState.Modified;
            db.SaveChanges();

            addActionToDB(Convert.ToInt32(info.user), Convert.ToInt32(info.project), "delete_user_story");

            //Task.Run(() => callNounPhraseExtractionModule(info.user, info.project));

            return RedirectToAction("Index", "Home");

        }


        public IActionResult deleteAllStories()
        {
            UserInfo info = HttpContext.Session.GetObject<UserInfo>("user");
            UserStory db = new UserStory();
            db.stories.Where(x => x.userID.ToString() == info.user && x.projectID.ToString() == info.project).ToList().ForEach(x => { x.isDeleted = true; db.Entry(x).State = EntityState.Modified; }) ;

            UserProject up = db.userProject.FirstOrDefault(x => x.userID.ToString() == info.user && x.projectID.ToString() == info.project);
            up.lastUserStorySaved = DateTime.Now;
            db.Entry(up).State = EntityState.Modified;
            db.SaveChanges();

            addActionToDB(Convert.ToInt32(info.user), Convert.ToInt32(info.project), "delete_all_user_stories");

            return RedirectToAction("Index", "Home");

        }

        public FileResult exportUserStories(string type)
        {
            UserStory db = new UserStory();
            UserInfo info = HttpContext.Session.GetObject<UserInfo>("user");

            var list = db.stories.Where(x => x.userID.ToString() == info.user && x.projectID.ToString() == info.project && !x.isDeleted).Select(x => new { x.storyID, x.userStory, x.saveDate, x.userID, x.projectID }).OrderBy(x => x.storyID).ToList();
            string fileType = "";
            string fileName = "user_stories";
            dynamic stream = null;

            if (type == "csv")
            {
                byte[] result;
                using (var memoryStream = new MemoryStream())
                {
                    using (var streamWriter = new StreamWriter(memoryStream))
                    {
                        using (var csvWriter = new CsvWriter(streamWriter, System.Globalization.CultureInfo.CurrentCulture))
                        {
                            csvWriter.WriteRecords(list);
                            streamWriter.Flush();
                            result = memoryStream.ToArray();
                        }
                    }
                }
                fileType = "text/csv";
                fileName += ".csv";
                stream = new FileStreamResult(new MemoryStream(result), "text/csv") { FileDownloadName = "user_stories.csv" }.FileStream;
            }

            else if (type == "json")
            {
                var result = JsonConvert.SerializeObject(list, new JsonSerializerSettings());
                fileType = "application/json";
                fileName += ".json";
                stream = Encoding.UTF8.GetBytes(result);
            }

            addActionToDB(Convert.ToInt32(info.user), Convert.ToInt32(info.project), "export_user_stories");

            return File(stream, fileType, fileName);


        }

    }
}