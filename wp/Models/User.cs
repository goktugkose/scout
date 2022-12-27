using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace wp_user_stories.Models
{
    public class User
    {
        [Key]
        public int userID { get; set; }
        public string? userName { get; set; }
        public int teamID { get; set; }
        public virtual Team team { get; set; }
        public virtual ICollection<Story> stories { get; set; }
        public virtual ICollection<UserProject> userProjects { get; set; }
        public virtual ICollection<Action> actions { get; set; }
    }
}