using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace wp_user_stories.Models
{
    public class Project
    {
        [Key]
        public int ProjectID { get; set; }
        public string? projectName { get; set; }

        public virtual ICollection<Story> stories { get; set; }
        public virtual ICollection<UserProject> userProjects { get; set; }

    }
}