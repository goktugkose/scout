using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace wp_user_stories.Models
{
    public class Story
    {        public Story()
        {
            this.saveDate = DateTime.Now;
        }

        [Key]
        public int storyID { get; set; }
        public string? userStory { get; set; }
        public DateTime saveDate { get; set; }

        public int userID { get; set; }
        [JsonIgnore]
        public virtual User user { get; set; }

        public int projectID { get; set; }

        public string? nounPhrases { get; set; }
        public string? verbPhrases { get; set; }
        
        public bool isDeleted { get; set; }

        [JsonIgnore]
        public virtual Project project { get; set; }

}
}