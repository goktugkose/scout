using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.SignalR;

namespace wp_user_stories.SignalHub
{
    public class CustomIdProvider : IUserIdProvider
    {
        readonly IHttpContextAccessor _httpContextAccessor;
        public CustomIdProvider(IHttpContextAccessor httpContextAccessor)
        {
            _httpContextAccessor = httpContextAccessor;
        }

        public string GetUserId(HubConnectionContext connection)
        {
            return _httpContextAccessor.HttpContext!.Request.Query["combinedId"];
        }
    }
}