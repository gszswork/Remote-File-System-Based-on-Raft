<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->




<!-- PROJECT LOGO -->
<br />
<p align="center">


  <h3 align="center">Flaks Based Remote File System</h3>

  <p align="center">
    This is a remote file system, mainly backend with a java based client toy-program. 
    The backend is developed in Flask framework. The backend server has been deployed on three Amazon Web Services (AWS) 
    nodes for system stability. To also keep the system consensus, raft algorithm is implemented. 
  </p>
</p>



## Backend API

You can connect to our file system by the [java_program](https://github.com/gszswork/Remote-File-System-Flask-Raft/blob/master/client/src/client/client.java), or just with the following command. 

The API is available online. Use it by sending your request to **http://18.119.17.134:801/{URI}** (One of the AWS nodes)

All interface are tested. You could test them [online](https://reqbin.com/) or using [Postman](https://www.postman.com/) (or using curl in command line).

Details are given below.

1. **/**
    ```
    URL: http://18.119.17.134:801/
    Method: GET
    Expected Return: {"code": 200, "result": "hi there"}
    ```
    The only function of this URI is to help you get your hands on RESTful API (or test your network connection). The number 200 means all is good. Basically, you could determine whether your request was successfully operated by the status code. You should never put anything into the HTTP request body when you use GET method. The format of message from the server would always be JSON (except when you wanna download a file).  

2. **/users/\<name\>/\<password\>**

    This interface is to allow a user to register or login.
    ```
    URL: http://18.119.17.134:801/users/<name>/<password>
    Method: GET, POST
    ```
    Use POST to register. For instance:
    ```
    curl -X POST http://18.119.17.134:801/users/test/testpassword
    ```
    This code is to register a user "test" with password "testpassword".

    Expected Return:
    ```
    {"code": 200, "result": "user registered successfully"}
    ```
    Other possible return:
    ```
    {"code": 304, "result": "user already exists"}
    ```

    Use GET to login.
    ```
    curl -X GET http://18.119.17.134:801/users/test/testpassword
    ```

    Expected Return:
    ```
    {"code": 200, "result": "user login successfully", "token": "7b873e9eeb11ced251401d1ed683ae3c"}
    ```
    Attach this token to every request below yo identify the user.

    Other possible return:
    ```
    {"code": 404, "result": "user does not exist"}
    ```
    or
    ```
    {"code": 403, "result": "wrong password"}
    ```

3. **/uploads/\<token\>**

    This interface is to upload a file or get the list of existing files.

    ```
    URL: http://18.119.17.134:801/uploads/<token>
    Method: GET, POST
    ```

    Use POST to upload a file to the server. There is a [demo](http://18.119.17.134:801/static/index.html) and here is an example [code](./static/example.java).

    Expected Return:
    ```
    {"code": 200, "result": "file uploaded successfully"}
    ```

    Use GET to obtain the list of existing files and files information.
    ```
    curl -X GET http://18.119.17.134:801/uploads/7b873e9eeb11ced251401d1ed683ae3c
    ```

    Expected Return:
    ```
    {"code": 200, "result": [{"name": "screenshot.png", "size": "853 KB", "mtime": "2020-05-07 09:30:24"}, {"name": "example.java", "size": "2 KB", "mtime": "2020-05-07 08:33:20"}]}
    ```

4. **/uploads/\<filename\>/\<token\>**

    This interface is to download or delete a file from the server.

    ```
    URL: http://18.119.17.134:801/uploads/<filename>/<token>
    Method: GET, DELETE
    ```

    Use GET to download a file.

    ```
    curl -X GET http://18.119.17.134:801/uploads/screenshot.png/7b873e9eeb11ced251401d1ed683ae3c
    ```

    Expected Return:
    ```
    The file itself.
    ```

    Other possible return:
    ```
    {"code": 404, "result": "file does not exist"}
    ```

    Use DELETE to delete a file.
    ```
    curl -X DELETE http://18.119.17.134:801/uploads/example.java/7b873e9eeb11ced251401d1ed683ae3c
    ```

    Expected Return:
    ```
    {"code": 200, "result": "file deleted successfully"}
    ```

    Other possible return:
    ```
    {"code": 404, "result": "file does not exist"}
    ```

5. **/uploads/\<oldfilename\>/\<newfilename\>/\<token\>**

    This interface is to change a file's name.

    ```
    URL: http://18.119.17.134:801/uploads/<oldfilename>/<newfilename>/<token>
    Method: PUT
    ```

    Use PUT to change filename.

    ```
    curl -X PUT http://18.119.17.134:801/uploads/screenshot.png/screenshot1.png/7b873e9eeb11ced251401d1ed683ae3c
    ```

    Expected Return:
    ```
    {"code": 200, "result": "file name changed successfully"}
    ```
    Other possible return:
    ```
    {"code": 404, "result": "file does not exist"}
    ```

6. **/sharedfiles/\<token\>**

    This interface is to obtain the list of shared files which are shared by other users.

    ```
    URL: http://18.119.17.134:801/sharedfiles/<token>
    Method: GET
    ```

    Use GET to obtain the list.

    ```
    curl -X GET http://18.119.17.134:801/sharedfiles/02938a072732bc44550c7639516414ed
    ```

    Expected Return:
    ```
    {"code": 200, "result": "shared files obtained successfully", "files": [{"from": "test", "filename": "example.java"}]}
    ```

7. **/sharedfiles/\<targetusername\>/\<filename\>/\<token\>**

    This interface is to accept, decline or create a sharing request.

    ```
    URL: http://18.119.17.134:801/sharedfiles/<targetusername>/<filename>/<token>
    Method: POST
    ```

    Use POST to share a file with another user.

    ```
    curl -X POST http://18.119.17.134:801/sharedfiles/atest/screenshot1.png/7b873e9eeb11ced251401d1ed683ae3c
    ```

    Expected Return:
    ```
    {"code": 200, "result": "file shared successfully"}
    ```

    Other possible return:
    ```
    {"code": 404, "result": "target user does not exist"}
    ```

    Use GET to accept a sharing request.

    ```
    curl -X GET http://18.119.17.134:801/sharedfiles/test/screenshot1.png/02938a072732bc44550c7639516414ed
    ```
    Expected Return:
    ```
    {"code": 200, "result": "file accepted successfully"}
    ```
    Other possible return:
    ```
    {"code": 404, "result": "file does not exist"}
    ```

    Use DELETE to decline a sharing request.

    ```
    curl -X DELETE http://18.119.17.134:801/sharedfiles/test/screenshot1.png/02938a072732bc44550c7639516414ed
    ```
    Expected Return:
    ```
    {"code": 200, "result": "file refused successfully"}
    ```
    Other possible return:
    ```
    {"code": 404, "result": "file does not exist"}
    ```




<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Your Name - danielkung1997@gmail.com

Project Link: [https://github.com/gszswork/Remote-File-System-Flask-Raft](https://github.com/gszswork/Remote-File-System-Flask-Raft)




