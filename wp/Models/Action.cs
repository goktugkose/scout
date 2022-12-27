using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace wp_user_stories.Models
{
    public class Action
    {
        [Key]
        public int actionID { get; set; }
        public string? type { get; set; }
        public DateTime actionTime { get; set; }
        public int userID { get; set; }
        [JsonIgnore]
        public virtual User user { get; set; }
        public int projectID { get; set; }
        [JsonIgnore]
        public virtual Project project { get; set; }
    }
}