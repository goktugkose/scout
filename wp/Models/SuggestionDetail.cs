using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Web;

namespace wp_user_stories.Models
{
    public class SuggestionDetail
    {
        [Key]
        public string suggestionGroup { get; set; }
        public string? mainSuggestionGroup { get; set; }
        public int suggestionScope { get; set; }
        public string? sugesstionType { get; set; }
        public string? suggestionExp { get; set; }
        public string? suggestionHint { get; set; }
        public string? suggestionName { get; set; }

    }
}