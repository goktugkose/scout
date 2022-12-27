using System;
using System.IO;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;
using wp_user_stories.SignalHub;

namespace wp_user_stories.Models
{
    public class DbOps
    {
    //     SqlCommand cmd;
    //     SqlDependency dependency;
    //      IConfigurationRoot configuration = new ConfigurationBuilder()
    //     .SetBasePath(Directory.GetCurrentDirectory())
    //     .AddJsonFile("appsettings.json")
    //     .Build();
    //     private bool disposedValue = false;
    //     public string getCommitsBehind(string userId, string projectId)
    //     {
    //         SqlDependency.Start(configuration.GetConnectionString("UserStory"));

    //         using (SqlConnection connection = new SqlConnection(configuration.GetConnectionString("UserStory")))
    //         {
    //             if (connection.State == System.Data.ConnectionState.Closed)
    //                 connection.Open();

    //             using (cmd = new SqlCommand(@"SELECT [actionID],[type],[actionTime],[userID],[projectID] FROM dbo.Actions where type = 'get_user_graph'", connection))
    //             {
    //                 cmd.Notification = null;
    //                 dependency = new SqlDependency(cmd);
    //                 dependency.OnChange += new OnChangeEventHandler((sender, e) => dependency_OnChange(sender, e, userId, projectId));
    //                 cmd.ExecuteNonQuery();

    //                 using (SqlCommand cmd2 = new SqlCommand(@"select COUNT(distinct actionTime) as commitsBehind from Actions where userID <> " + userId + " and projectID = " + projectId + " and type = 'get_user_graph' and actionTime > (select MAX(actionTime) from Actions where userID = " + userId + " and projectID = " + projectId + " and type = 'get_user_graph')", connection))
    //                 {
    //                     int result = Convert.ToInt32(cmd2.ExecuteScalar());
    //                     return "The model has been changed " + result + " times by other users. You may consider asking for more suggestions.";
    //                 }
    //             }
    //         }
    //     }
    //     public void dependency_OnChange(object sender, SqlNotificationEventArgs e, string userId, string projectId)
    //     {
    //         dependency.OnChange-=new OnChangeEventHandler((sender, e) => dependency_OnChange(sender, e, userId, projectId));
    //         //MessageHub m = new MessageHub();
    //         //m.Send(userId + "_" + projectId);
    //     }

    //     #region IDisposable

    // ~DbOps()
    // {
    //     Dispose(false);
    // }

    // protected virtual void Dispose(bool disposing)
    // {
    //     if (!disposedValue)
    //     {
    //         if (disposing)
    //         {
    //             SqlDependency.Stop(configuration.GetConnectionString("UserStory"));
    //         }

    //         disposedValue = true;
    //     }
    // }

    // public void Dispose()
    // {
    //     Dispose(true);
    //     GC.SuppressFinalize(this);
    // }

    // #endregion
     }
}