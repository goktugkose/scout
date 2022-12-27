using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using System.IO;

namespace wp_user_stories.Models
{
    public class UserStory : DbContext
    {
        // Your context has been configured to use a 'UserStory' connection string from your application's 
        // configuration file (App.config or Web.config). By default, this connection string targets the 
        // 'wp_user_stories.Models.UserStory' database on your LocalDb instance. 
        // 
        // If you wish to target a different database and/or database provider, modify the 'UserStory' 
        // connection string in the application configuration file.
        
        public UserStory()
        {

        }
        public UserStory(DbContextOptions<UserStory> options):base(options)
        {

        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            new DbInitializer(modelBuilder).Seed();
        }

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            if (!optionsBuilder.IsConfigured)
            {
                IConfigurationRoot configuration = new ConfigurationBuilder()
                   .SetBasePath(Directory.GetCurrentDirectory())
                   .AddJsonFile("appsettings.json")
                   .Build();
                var connectionString = configuration.GetConnectionString("UserStory");
                optionsBuilder.UseSqlServer(connectionString);
                optionsBuilder.EnableSensitiveDataLogging(true);
                optionsBuilder.UseLazyLoadingProxies();
            }
        }

        /*protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            //Database.SetInitializer<UserStory>(new Strategy());
            //modelBuilder.Conventions.Remove<OneToManyCascadeDeleteConvention>();
        }*/

        public virtual DbSet<Story> stories { get; set; }
        public virtual DbSet<User> users { get; set; }
        public virtual DbSet<Project> projects { get; set; }
        public virtual DbSet<Team> teams { get; set; }
        public virtual DbSet<UserProject> userProject { get; set; }
        public virtual DbSet<Action> actions { get; set; }
        public virtual DbSet<Notification> notifications { get; set; }
        public virtual DbSet<Suggestion> suggestions { get; set; }
        public virtual DbSet<Scenario> scenarios { get; set; }
        public virtual DbSet<SuggestionDetail> suggestionDetails { get; set; }
        public virtual DbSet<IgnoredSuggestion> IgnoredSuggestions { get; set; }

        // Add a DbSet for each entity type that you want to include in your model. For more information 
        // on configuring and using a Code First model, see http://go.microsoft.com/fwlink/?LinkId=390109.

        // public virtual DbSet<MyEntity> MyEntities { get; set; }
    }

    //public class MyEntity
    //{
    //    public int Id { get; set; }
    //    public string Name { get; set; }
    //}
}