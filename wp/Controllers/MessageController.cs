using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.SignalR;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Data.SqlClient;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using wp_user_stories.Models;
using wp_user_stories.SignalHub;

namespace wp_user_stories.Controllers
{
    [AllowAnonymous]
    public class MessageController : Controller
    {
        public string getHost(){
            IConfigurationRoot configuration = new ConfigurationBuilder()
           .SetBasePath(Directory.GetCurrentDirectory())
           .AddJsonFile("appsettings.json")
           .Build();
            return configuration.GetValue<string>("ws-host");
        }
        public JsonResult returnScenario(int scenarioGroup)
        {
            UserStory db = new UserStory();
            string scenarioText = db.scenarios.Where(x => x.scenarioGroup == scenarioGroup).FirstOrDefault().scenarioLink;
            return Json(scenarioText);
        }

        public JsonResult setIgnoredSuggestion(int storyId, string term, string suggestionGroup, int userID, int projectID, string mainTerm)
        {
            UserStory db = new UserStory();
            suggestionGroup = suggestionGroup.Trim();
            mainTerm =  mainTerm != null ? mainTerm.Trim() : mainTerm;
            term = term.Trim();
            db.IgnoredSuggestions.Add(new IgnoredSuggestion()
            {
                user = db.users.Where(x => x.userID == userID).FirstOrDefault(),
                project = db.projects.Where(x => x.ProjectID == projectID).FirstOrDefault(),
                story = db.stories.Where(x => x.storyID == storyId).FirstOrDefault(),
                suggestionDetail = db.suggestionDetails.Where(x => x.suggestionGroup == suggestionGroup).FirstOrDefault(),
                mainTerm = mainTerm,
                term = term
            });
            db.SaveChanges();
            return Json(true);
        }

        public JsonResult saveMessages(string userId, string userName, string projectId, string message)
        {
            UserStory db = new UserStory();
            db.notifications.Add(new Notification()
            {
                userId = Convert.ToInt32(userId),
                userName = userName,
                projectId = Convert.ToInt32(projectId),
                message = message,
                time = DateTime.Now
            });
            db.SaveChanges();
            return Json(true);
        }

        public async Task<JsonResult> getSuggestions(string user_id, string project_id)
        {
            string host = getHost();
            var url = "http://"+host+"/unrelated_suggestions?user_id=" + user_id + "&project_id=" + project_id;
            Stream t1 = null;

            using (var client = new HttpClient())
            {
                t1 = await client.GetStreamAsync(url);
            }

            string responseString = new StreamReader(t1).ReadToEnd();
            return Json(responseString);
        }

        public async Task<JsonResult> getAllSuggestions(string user_id, string project_id)
        {
            string host = getHost();
            var url = "http://"+host+"/all_suggestions?user_id=" + user_id + "&project_id=" + project_id;

            Stream t1 = null;

            using (var client = new HttpClient())
            {
               t1 = await client.GetStreamAsync(url);
            }

            string responseString = new StreamReader(t1).ReadToEnd();
            return Json(responseString);
        }

        public async Task<JsonResult> runGraphModule(string user_id, string project_id)
        {
            string host = getHost();
			var url = "http://"+host+"/noun_phrase_extraction?user_id=" + user_id + "&project_id=" + project_id;
            string url1 = "http://"+host+"/get_user_graph?user_id=" + user_id + "&project_id=" + project_id;
            string url2 = "http://"+host+"/get_project_graph?user_id=" + user_id + "&project_id=" + project_id;

            Task t1, t2 = null;

			using (var client = new HttpClient())
            {
				 string t0 = await client.GetStringAsync(url);
                 t1 = client.GetStringAsync(url1);
                 t2 = client.GetStringAsync(url2);

                List<Task> tasks = new List<Task>() { t1, t2 };
                await Task.WhenAll(tasks);
            }            

            return Json(true);
        }

        public JsonResult getChatMessages(string project_id)
        {
            UserStory db = new UserStory();
            List<Notification> notifications = db.notifications.ToList(); 

            return Json(
                notifications.Where(x => x.projectId == Convert.ToInt32(project_id))
                .Select(x => new {
                    userName = x.userName,
                    time = x.time.ToString(),
                    message = x.message
                }).OrderBy(x => x.time).ToList()
            );
        }
    }
}