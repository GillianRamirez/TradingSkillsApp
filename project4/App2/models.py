from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=150)
    content = models.TextField()

    def __str__(self):
        return self.title
    
    
class StockPortfolio(models.Model):
    user_id = models.IntegerField()
    stock_id = models.CharField(max_length=100)
    shares = models.IntegerField(default=0)
    share_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Portfolio: {self.stock_id}"
    

class PortfolioItem(models.Model):
    company_name = models.CharField(max_length=100)
    stock_price = models.DecimalField(max_digits=10, decimal_places=2)