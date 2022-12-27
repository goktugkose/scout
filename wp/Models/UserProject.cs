using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace wp_user_stories.Models
{
    public class UserProject
    {
        [Key]
        public int userProjectID { get; set; }
        public int userID { get; set; }
        public int projectID { get; set; }
        public int scenarioGroup { get; set; }
        //public DateTime? lastGraphSaved { get; set; }
        public DateTime? lastUserStorySaved { get; set; }
        public DateTime? lastSuggestionGathered { get; set; }

        public virtual User user { get; set; }
        public virtual Project project { get; set; }
    }
}