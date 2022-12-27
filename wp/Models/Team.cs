using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace wp_user_stories.Models
{
    public class Team
    {
        [Key]
        public int teamID { get; set; }
        public string? teamName { get; set; }

        public virtual ICollection<User> users { get; set; }
    }
}