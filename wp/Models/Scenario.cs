using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace wp_user_stories.Models
{
    public class Scenario
    {
        [Key]
        public int scenarioID { get; set; }
        public int scenarioGroup { get; set; }
        public string? scenarioLink { get; set; }
    }
}