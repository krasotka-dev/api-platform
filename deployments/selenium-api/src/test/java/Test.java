import apiModels.RequestBody;
import apiModels.ResponseBody;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.restassured.RestAssured;
import io.restassured.response.Response;
import utilities.APIUtil;
import utilities.Config;

public class Test {
    ;

    @org.junit.Test
    public void test1() throws Exception {
        String url = Config.getProperty("baseURL");
        Response response = RestAssured.get(url);
        System.out.println(response.statusCode());
        System.out.println(response.asString());

        ObjectMapper objectMapper = new ObjectMapper();
        RequestBody requestBody=  objectMapper.readValue(response.asString(), RequestBody.class);
        System.out.println(requestBody.getEmail());

    }


    @org.junit.Test
    public void test2(){
        APIUtil.hitGET("");

    }

}
