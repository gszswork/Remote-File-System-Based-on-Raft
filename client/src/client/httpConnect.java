package client;
import java.io.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Vector;

import org.apache.http.*;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import org.apache.http.impl.client.*;
import org.apache.http.util.*;
import org.apache.http.client.methods.*;
import org.apache.http.entity.mime.MultipartEntityBuilder;


public class httpConnect {
	private static CloseableHttpClient httpClient =HttpClientBuilder.create().build();
	private static CloseableHttpResponse response = null;
	//private static String url="http://api.boyang.website/";
	private static String token;
	private JSONParser parser = new JSONParser();
	private String[] ipList= {"18.117.80.212","18.119.17.134","18.223.255.142"};
	private String port = "801";
//{"115.146.94.191",  "115.146.93.126","139.180.172.244"};

    public httpConnect() {
    	
    }
    private String accessLeader(String url) {
    	System.out.println("SHUZHI: "+ url);
    	try {
    		String uri="leader";
    		url="http://"+url+':'+port+"/"+uri;
    		System.out.println(url);
    		
    		HttpGet httpGet = new HttpGet(url);
    		 
    		
    		response = httpClient.execute(httpGet);
    		int statusCode = response.getStatusLine().getStatusCode();
			HttpEntity responseEntity = response.getEntity();
			String responseString = EntityUtils.toString(responseEntity, "UTF-8");
			
			System.out.println("[" + statusCode + "] " + responseString);
			JSONObject request = (JSONObject) parser.parse(responseString);
			int code =  Integer.parseInt(String.valueOf(request.get("code")));
			if (code == 200) {
    			return String.valueOf(request.get("result"));
    		}
    	}catch (Exception e) {
    		System.out.println("access exception");
    		//e.printStackTrace();
    	}
    	return "null";
    }
    public String login(String username, String password, String url) {
    	try {	
    		String uri="users/"+username+"/"+password;
//    		url="http://"+url+"/"+uri;
    		System.out.println("http://"+url+"/"+uri);
    		HttpGet httpGet=new HttpGet("http://"+url+':'+port+"/"+uri); //login
    		response = httpClient.execute(httpGet);
    		String res = EntityUtils.toString(response.getEntity());
    		System.out.println("login "+ res);
			JSONObject request = (JSONObject) parser.parse(res);
			int code =  Integer.parseInt(String.valueOf(request.get("code")));
    		if (code==200) {
    			// login successfully
    			// get the token
    			token =(String) request.get("token"); 
    			System.out.println("token "+token);
    			return "login";
                
            } else if (code==404){
                //user does not exist, register
            	HttpPost httpPost = new HttpPost("http://"+url+':'+port+"/"+uri);
            	CloseableHttpResponse response2 = httpClient.execute(httpPost);
            	String res2 = EntityUtils.toString(response2.getEntity());
        		System.out.println("register "+res2);
    			JSONObject request2 = (JSONObject) parser.parse(res2);
    			int code2 =  Integer.parseInt(String.valueOf(request2.get("code")));
            	if (code2 == 200) {
            		// register successfully
            		System.out.println("register successfully");
            		return "register";
            	}else {
            		// user already exists
            		System.out.println("user already exists");
            		return "error0";
            	}	
            }else if(code==503){
            	String result=accessLeader(url);
            	if (result=="null") {
            		String newLeader=getLeader();
            		if(newLeader=="None") {
            			return "fail";
            		}else {
            			return login(username,  password, newLeader);	
            		}
            	}
            }else {
            	//wrong password
            	System.out.println("wrong password");
            	return "error1";
            }
    	}catch (Exception e) {
    		System.out.println("login exception"+ e);
    		//e.printStackTrace();
    	}
    	return "error2";
    }
    public void init(Vector<Vector> data, String url) {
    	try {
    		//data=new Vector<Vector>();
    		String uri="uploads/"+token;
    		System.out.println("initiate data "+"http://"+url+':'+port+"/"+uri);
    		HttpGet httpGet = new HttpGet("http://"+url+':'+port+"/"+uri);
    		response = httpClient.execute(httpGet);
    		String res = EntityUtils.toString(response.getEntity());
			//JSONParser parser = new JSONParser();
			JSONObject request = (JSONObject) parser.parse(res);
			System.out.println("initiate data "+res);
			int code =  Integer.parseInt(String.valueOf(request.get("code")));
    		if (code == 200) {
    			// file uploaded successfully
    			List result =(List) request.get("result"); 
    			for(int i=0;i<result.size();i++) {
    				String line=result.get(i).toString();
    				System.out.println(line);
    				JSONObject linedata = (JSONObject) parser.parse(line);
    				String name=(String) linedata.get("name");
    				String size=(String) linedata.get("size");
    				String time=(String) linedata.get("mtime");
    				Vector newVector=new Vector();
    				newVector.add(false);
    				newVector.add(name);
    				newVector.add(size);
    				newVector.add(time);
    				data.add(newVector);
    			}
            } 
    	}catch (Exception e) {
    		System.out.println("init exception");
    		//e.printStackTrace();
    	}
    }
    public String upload(File file, String url) {
    	try {
    		String uri="uploads/"+token;
//    		url="http://"+url+"/"+uri;
    		System.out.println("http://"+url+':'+port+"/"+uri);
    		
    		HttpPost httpPost = new HttpPost("http://"+url+':'+port+"/"+uri);
    		FileInputStream fis = new FileInputStream(file);
    		MultipartEntityBuilder multipartEntityBuilder = MultipartEntityBuilder.create();  
    		multipartEntityBuilder.addBinaryBody("file",file);
    		HttpEntity httpEntity = multipartEntityBuilder.build();
    		    
    		httpPost.setEntity(httpEntity);  
    		
    		response = httpClient.execute(httpPost);
    		int statusCode = response.getStatusLine().getStatusCode();
			HttpEntity responseEntity = response.getEntity();
			String responseString = EntityUtils.toString(responseEntity, "UTF-8");
			
			System.out.println("[" + statusCode + "] " + responseString);

//    		System.out.println(55555);
//    		String res = EntityUtils.toString(response.getEntity());
//    		System.out.println(66666+res);
//			
			JSONObject request = (JSONObject) parser.parse(responseString);		
			int code =  Integer.parseInt(String.valueOf(request.get("code")));
    		if (code == 200) {
    			// file uploaded successfully
    			System.out.println("file uploaded successfully"); 
    			return "success";
            } else {
            	String result=accessLeader(url);
            	if (result=="null") {
            		String newLeader=getLeader();
            		if(newLeader=="None") {
            			return "fail";
            		}else {
            			return upload(file, newLeader);	
            		}
            	}
            }
    	}catch (Exception e) {
    		System.out.println("exception");
    	}
    	return "error";
    }
    public InputStream download(String file, String url) {
    	try {
    		String uri="uploads/"+file+"/"+token;
    		System.out.println("http://"+url+':'+port+"/"+uri);
    		
    		HttpGet httpGet = new HttpGet("http://"+url+':'+port+"/"+uri);
    		 
    		
    		response = httpClient.execute(httpGet);
    		
    		int statusCode = response.getStatusLine().getStatusCode();
			HttpEntity responseEntity = response.getEntity();
			InputStream is = responseEntity.getContent();
			return is;
    	}catch (Exception e) {
    		System.out.println("download exception");
    		//e.printStackTrace();
    	}
    	return null;
    }

    public String delete(String file, String url) {
    	try {
    		String uri="uploads/"+file+"/"+token;
    		System.out.println("http://"+url+':'+port+"/"+uri);
    		
    		HttpDelete httpDelete = new HttpDelete("http://"+url+':'+port+"/"+uri);
    		 
    		
    		response = httpClient.execute(httpDelete);
    		int statusCode = response.getStatusLine().getStatusCode();
			HttpEntity responseEntity = response.getEntity();
			String responseString = EntityUtils.toString(responseEntity, "UTF-8");
			
			System.out.println("[" + statusCode + "] " + responseString);
			JSONObject request = (JSONObject) parser.parse(responseString);		
			int code =  Integer.parseInt(String.valueOf(request.get("code")));
    		if (code == 200) {
    			// file deleted successfully
    			System.out.println("file deleted successfully"); 
    			return "success";
            } else {
            	String result=accessLeader(url);
            	if (result=="null") {
            		String newLeader=getLeader();
            		if(newLeader=="None") {
            			return "fail";
            		}else {
            			return delete(file, newLeader);	
            		}
            	}
            }
    	}catch (Exception e) {
    		System.out.println("delete exception");
    		//e.printStackTrace();
    	}
    	return "error";
    }
    public String rename(String oldFile, String newFile, String url) {
    	try {
    		String uri="uploads/"+oldFile+"/"+newFile+"/"+token;
//    		url="http://"+url+"/"+uri;
    		System.out.println("http://"+url+':'+port+"/"+uri);
    		
    		HttpPut httpPut = new HttpPut("http://"+url+':'+port+"/"+uri);
    		 
    		
    		response = httpClient.execute(httpPut);
    		int statusCode = response.getStatusLine().getStatusCode();
			HttpEntity responseEntity = response.getEntity();
			String responseString = EntityUtils.toString(responseEntity, "UTF-8");
			
			System.out.println("[" + statusCode + "] " + responseString);
			JSONObject request = (JSONObject) parser.parse(responseString);		
			int code =  Integer.parseInt(String.valueOf(request.get("code")));
    		if (code == 200) {
    			// file renamed successfully
    			System.out.println("file renamed successfully"); 
    			return "success";
            } else if (code==503){
            	String result=accessLeader(url);
            	if (result=="null") {
            		String newLeader=getLeader();
            		if(newLeader=="None") {
            			return "fail";
            		}else {
            			return rename(oldFile, newFile, newLeader);	
            		}
            	}
            }
    	}catch (Exception e) {
    		System.out.println("delete exception");
    		//e.printStackTrace();
    	}
    	return "error";
    }
    public String share(String targetUsername, String filename, String url) {
    	try {
    		String uri="sharedfiles/"+targetUsername+"/"+filename+"/"+token;
    		///////
    		System.out.println("http://"+url+':'+port+"/"+uri);
    		
    		HttpPost httpPost = new HttpPost("http://"+url+':'+port+"/"+uri);
    		 
    		
    		response = httpClient.execute(httpPost);
    		int statusCode = response.getStatusLine().getStatusCode();
			HttpEntity responseEntity = response.getEntity();
			String responseString = EntityUtils.toString(responseEntity, "UTF-8");
			
			System.out.println("[" + statusCode + "] " + responseString);
			JSONObject request = (JSONObject) parser.parse(responseString);
			int code =  Integer.parseInt(String.valueOf(request.get("code")));
    		if (code == 200) {
    			return "success";
    		}else if(code==404){
    			return "not exist";
    		}else if(code==503){
            	String result=accessLeader(url);
            	if (result=="null") {
            		String newLeader=getLeader();
            		if(newLeader=="None") {
            			return "fail";
            		}else {
            			return share(targetUsername, filename, newLeader);	
            		}
            	}
            }
    	}catch (Exception e) {
    		System.out.println("share exception");
    		//e.printStackTrace();
    	}
    	return "error";
    }
    public String acceptShare(String targetUsername, String filename, String url) {
    	try {
    		String uri="sharedfiles/"+targetUsername+"/"+filename+"/"+token;
//    		url="http://"+url+"/"+uri;
    		System.out.println("http://"+url+':'+port+"/"+uri);
    		
    		HttpGet httpGet = new HttpGet("http://"+url+':'+port+"/"+uri);
    		 
    		
    		response = httpClient.execute(httpGet);
    		int statusCode = response.getStatusLine().getStatusCode();
			HttpEntity responseEntity = response.getEntity();
			String responseString = EntityUtils.toString(responseEntity, "UTF-8");
			
			System.out.println("[" + statusCode + "] " + responseString);
			JSONObject request = (JSONObject) parser.parse(responseString);
			int code =  Integer.parseInt(String.valueOf(request.get("code")));
    		if (code == 200) {
    			return "success";
    		}else if(code==503){
            	String result=accessLeader(url);
            	if (result=="null") {
            		String newLeader=getLeader();
            		if(newLeader=="None") {
            			return "fail";
            		}else {
            			return acceptShare(targetUsername, filename, newLeader);	
            		}
            	}
            }
    	}catch (Exception e) {
    		System.out.println("accept share exception");
    		//e.printStackTrace();
    	}
    	return "error";
    }
    public String declineShare(String targetUsername, String filename, String url) {
    	try {
    		String uri="sharedfiles/"+targetUsername+"/"+filename+"/"+token;
    		System.out.println("http://"+url+':'+port+"/"+uri);
    		
    		HttpDelete httpDelete = new HttpDelete("http://"+url+':'+port+"/"+uri);
    		 
    		
    		response = httpClient.execute(httpDelete);
    		int statusCode = response.getStatusLine().getStatusCode();
			HttpEntity responseEntity = response.getEntity();
			String responseString = EntityUtils.toString(responseEntity, "UTF-8");
			
			System.out.println("[" + statusCode + "] " + responseString);
			JSONObject request = (JSONObject) parser.parse(responseString);
			int code =  Integer.parseInt(String.valueOf(request.get("code")));
    		if (code == 200) {
    			return "success";
    		}else if(code==503){
            	String result=accessLeader(url);
            	if (result=="null") {
            		String newLeader=getLeader();
            		if(newLeader=="None") {
            			return "fail";
            		}else {
            			return declineShare(targetUsername, filename, newLeader);	
            		}
            	}
            }
    	}catch (Exception e) {
    		System.out.println("decline share exception");
    		//e.printStackTrace();
    	}
    	return "error";
    }
    public ArrayList<List> receive(String url) {
    	ArrayList<List> list=new ArrayList<List>();
    	try {
    		String uri="sharedfiles/"+token;
//    		url="http://"+url+"/"+uri;
    		System.out.println("http://"+url+':'+port+"/"+uri);
    		
    		HttpGet httpGet = new HttpGet("http://"+url+':'+port+"/"+uri);
    		 
    		
    		response = httpClient.execute(httpGet);
    		int statusCode = response.getStatusLine().getStatusCode();
			HttpEntity responseEntity = response.getEntity();
			String responseString = EntityUtils.toString(responseEntity, "UTF-8");
			
			System.out.println("[" + statusCode + "] " + responseString);
			
			JSONObject request = (JSONObject) parser.parse(responseString);
			
			int code =  Integer.parseInt(String.valueOf(request.get("code")));
			
    		if (code == 200) {
    			// file uploaded successfully
    			List result =(List) request.get("files"); 
    			if(result.size()>0) {
    				for(int i=0;i<result.size();i++) {
        				String line=result.get(i).toString();
        				System.out.println(line);
        				JSONObject linedata = (JSONObject) parser.parse(line);
        				String from=(String) linedata.get("from");
        				String filename=(String) linedata.get("filename");
        				List<String> l=Arrays.asList(from, filename);
        				list.add(l);
        			}
    			}else {
    				//list=null;
    				return list;
    			}
            } 
    	}catch (Exception e) {
    		System.out.println("receive exception");
    		//e.printStackTrace();
    	}
    	//list=null;
    	return list;
    }
    
    public String getLeader() {
		String leader="null";
		for(String ip:ipList) {
			leader=accessLeader(ip);
			if(leader=="null") {
				continue;
			}else {
				break;
			}
		}
		if(leader=="null") {
			return "None";
			//System.exit(-1);
		}else {
			return leader;
		}
	}

}
