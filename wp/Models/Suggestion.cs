using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace wp_user_stories.Models
{
    public class Suggestion
    {
        public Suggestion()
        {
            this.saveDate = DateTime.Now;
        }
        [Key]
        public int suggestionID { get; set; }
        public int userID { get; set; }
        public int projectID { get; set; }
        public string? suggestionGroup { get; set; }
        public int storyID { get; set; }
        public DateTime saveDate { get; set; }
        public string? mainTerm { get; set; }
        public string? term { get; set; }
        public bool isProjectWide { get; set; }
        public virtual User user { get; set; }
        public virtual Project project { get; set; }
        public virtual SuggestionDetail suggestionDetail { get; set; }
    }
}