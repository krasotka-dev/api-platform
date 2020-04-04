package utilities;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebDriverException;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.safari.SafariDriver;

public class Driver {

    private static WebDriver driver;

    private Driver() {

    }

    public static WebDriver getReference(){
        return driver;
    }

    public static WebDriver getDriver() {

        if (driver == null) {

            String browser = Config.getProperty("browser");

            if ("chrome".equals(browser)) {

                WebDriverManager.chromedriver().setup();
                driver = new ChromeDriver();

            }
            else if ("firefox".equals(browser)) {
                WebDriverManager.firefoxdriver().setup();
                driver = new FirefoxDriver();
            }
            else if ("safari".equals(browser)) {
                if (System.getProperty("os.name").toLowerCase().contains("windows")) {
                    throw new WebDriverException("Windows OS does not support safari");
                }
                WebDriverManager.getInstance(SafariDriver.class).setup();
                driver = new SafariDriver();
            }

            //driver.manage().timeouts().implicitlyWait(10, TimeUnit.SECONDS);
            driver.manage().window().maximize();

        }

        return driver;

    }

    public static void quitDriver() {
        if (driver != null) {
            driver.quit();
            driver = null;
        }
    }

}
