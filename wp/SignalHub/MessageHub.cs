using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.SignalR;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Web;

namespace wp_user_stories.SignalHub
{
    public class MessageHub : Hub
    {
        public void SendNotification(string userName, string projectId, string message)
        {
            Clients.Group(projectId).SendAsync("receiveNotification", userName, message, DateTime.Now.ToString());
        }
         
        public override Task OnConnectedAsync()
        {
            string groupId = Context.GetHttpContext()!.Request.Query["combinedId"].ToString().Split('_')[1];
            return Groups.AddToGroupAsync(Context.ConnectionId, groupId);
        }


        public override async Task OnDisconnectedAsync(Exception? ex)
        {
            string groupId = Context.GetHttpContext()!.Request.Query["combinedId"].ToString().Split('_')[1];
            await Groups.RemoveFromGroupAsync(Context.ConnectionId, groupId);
            await base.OnDisconnectedAsync(ex);
        }
    }
}