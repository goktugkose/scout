using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using wp_user_stories.Models;

namespace wp_user_stories.Views.Login.ViewModels
{
    public class UserInfo
    {
        public string user { get; set; } = null!;
        public string project { get; set; } = null!;
        public int scenarioGroup { get; set; }
        public bool isGraphUpdated { get; set; }
        public bool isSuggestionsUpdated { get; set; }

    }
}