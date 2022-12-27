using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace wp_user_stories.Models
{
    public class Notification
    {
        [Key]
        public int notificationId { get; set;}
        public int userId { get; set;}
        public string? userName { get; set; }
        [JsonIgnore]
        public virtual User user { get; set; }
        public int projectId { get; set; }
        [JsonIgnore]
        public virtual Project project { get; set; }
        public string? message { get; set; }
        public DateTime time { get; set; }
    }
}