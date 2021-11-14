package client;

import mdlaf.*;
import mdlaf.animation.*;
import mdlaf.utils.*;
import mdlaf.components.*;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.List;
import java.util.Timer;

public class client {
	private String username;
	private String password;
	private JFrame frame;
	Font font = new Font("monospaced",Font.ITALIC,10);
	private JTable table;
	private Vector<Vector> data=new Vector();
	private Vector<Vector> searchedData=new Vector();;
	private checkTable tableModel;
	private JTextField textField;
	//private String[] ipList= {"115.146.94.191",  "115.146.93.126","139.180.172.244"};
	private String leaderIP;
	private boolean searchOrNot=false;
	private httpConnect connect=new httpConnect();
//	private String token;
	

	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
//					try {
//						UIManager.setLookAndFeel (new MaterialLookAndFeel ());
//					}
//					catch (UnsupportedLookAndFeelException e) {
//						e.printStackTrace ();
//					}
					client window = new client();
					
//					window.frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the application.
	 */
	public client() {
		initialize();
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		while(true) {
			username  = JOptionPane.showInputDialog(
					"Input your name",
					"Default"
			);
			//check whether username in database
			if(username==null) {
				System.exit(0);
			}
			password  = JOptionPane.showInputDialog(
					"Input your password",
					"Default"
			);
			//check whether password is right
			if(password==null) {
				System.exit(0);
			}
			leaderIP=connect.getLeader();
			System.out.println("leaderIP: "+leaderIP);
			String result=connect.login(username, password, leaderIP);
			
			System.out.println("login "+result);
			if(result.equals("error0")) {
				JOptionPane.showMessageDialog(null, "Registration fails. User already exists. Try again!","Notice", JOptionPane.ERROR_MESSAGE);
				continue;
			}
			else if(result.equals("error1")) {
				JOptionPane.showMessageDialog(null, "Login fails. Wrong password. Try again!","Notice", JOptionPane.ERROR_MESSAGE);
				continue;
			}
			else if(result.equals("error2")) {
				JOptionPane.showMessageDialog(null, "Error. Try again!","Notice", JOptionPane.ERROR_MESSAGE);
				continue;
			}else if(result.equals("register")) {
				JOptionPane.showMessageDialog(null, "Register successfully");
				connect.login(username, password, leaderIP);
				break;
			}else if(result.equals("fail")){
				JOptionPane.showMessageDialog(null, "Server broken down","Notice", JOptionPane.ERROR_MESSAGE);
				break;
			}else{
//				token=result;
				initData();
				System.out.println("Login successfully");
				break;
			}
		
		}
		
		JFrame frame = new JFrame ("Dropbox");
		frame.setMinimumSize (new Dimension(900, 600));

		JPanel content = new JPanel ();
		content.setLayout(null);
		JButton btnUpload = new JButton("Upload");
//		btnUpload.setPreferredSize(new Dimension(29,29));
		btnUpload.setBounds(6, 19, 117, 29);
		frame.getContentPane().add(btnUpload);
//		content.add(btnUpload);
		
		JButton btnDownload = new JButton("Download");
//		content.add(btnDownload);
		frame.getContentPane().add(btnDownload);
		btnDownload.setBounds(135, 19, 117, 29);

		JButton btnRename = new JButton("Rename");
		frame.getContentPane().add(btnRename);
//		content.add(btnRename);
		btnRename.setBounds(238, 19, 117, 29);
		JButton btnDelete = new JButton("Delete");
		frame.getContentPane().add(btnDelete);
//		content.add(btnDelete);
		btnDelete.setBounds(342, 19, 117, 29);
		
		JButton btnShare = new JButton("Share");
		btnShare.setBounds(444, 19, 117, 29);
		frame.getContentPane().add(btnShare);
//		content.add(btnShare);
		
		frame.getContentPane().add (content, BorderLayout.CENTER);
		
		table = new JTable();
		
		
		JScrollPane scrollPane = new JScrollPane(table,JScrollPane.VERTICAL_SCROLLBAR_ALWAYS,JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);
		scrollPane.setBounds(6, 51, 888, 498);
		content.add(scrollPane);
		
		textField = new JTextField();
		textField.setBounds(614, 17, 143, 29);
		content.add(textField);
		textField.setColumns(10);
		
		JButton btnSearch = new JButton("Search");
		btnSearch.setBounds(777, 17, 117, 29);
		content.add(btnSearch);
		
		JLabel lblNewLabel = new JLabel("Server: "+leaderIP);
		lblNewLabel.setBounds(16, 556, 603, 16);
		content.add(lblNewLabel);
		
		initTable(data);
		
		btnUpload.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if (searchOrNot) {
					
				}else {
					try {
						JFileChooser chooser=new JFileChooser();
						int temp=chooser.showOpenDialog(frame);
						//setFileChooserFont(chooser.getComponents());
						File file =chooser.getSelectedFile();

						if(file!=null && temp==JFileChooser.APPROVE_OPTION) {

							String filename=file.getName();
							String filesize=getFileSize(file);
							boolean flag=false;
							for(int i=0;i<data.size();i++) {
								System.out.println(1);
								System.out.println(data.get(i).get(1));
								if(data.get(i).get(1).equals(filename)) {
									JOptionPane.showMessageDialog(null, "File already exists","Notice", JOptionPane.ERROR_MESSAGE);
									flag=true;
									break;
								}
							}
							if(!flag) {
								//addData(filename,filesize,getTime());
								
								//*****TO DO*****
								//transfer filename to server
								String result=connect.upload(file, leaderIP);
								if(result.contentEquals("fail")) {
									JOptionPane.showMessageDialog(null, "Server broken down","Notice", JOptionPane.ERROR_MESSAGE);
								}else if(result.equals("error")) {
									JOptionPane.showMessageDialog(null, "Upload fails","Notice", JOptionPane.ERROR_MESSAGE);
								}else if(result.equals("success")) {
									initData();
									initTable(data);
								}
							}
							
						}
							
					} catch (Exception e1) {
						e1.printStackTrace();
					}
				
				}
			}
		});
		btnDownload.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				
				if(searchOrNot) {//in search state
					List indexList=getSelectedIndex(searchedData);
					if(indexList.size()==0) {
						JOptionPane.showMessageDialog(null, "Please select one file to download","Notice", JOptionPane.ERROR_MESSAGE);
					}else {
						List<String> filenameList=new ArrayList<String>();
						for(int i=0;i<indexList.size();i++) {
							filenameList.add((String) searchedData.get((int)indexList.get(i)).get(1));
						}
						//****TO DO*****
						//transfer filenameList to download to server
						//receive file from server
					}
				}else {
					List indexList=getSelectedIndex(data);
					if(indexList.size()==0) {
						JOptionPane.showMessageDialog(null, "Please select one file to download","Notice", JOptionPane.ERROR_MESSAGE);
					}else {
						List<String> filenameList=new ArrayList<String>();
						for(int i=0;i<indexList.size();i++) {
							filenameList.add((String) data.get((int)indexList.get(i)).get(1));
						}
						//****TO DO*****
						//transfer filenameList to download to server
						//receive file from server
						try {
							JFileChooser fc=new JFileChooser();
							fc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
							int temp=fc.showOpenDialog(null);
							
							File f=fc.getSelectedFile();
							if(f!=null&&temp==JFileChooser.APPROVE_OPTION) {
								for(String filename: filenameList) {
									String filePath=f.getPath()+File.separator+filename;
									File file=new File(filePath);
									InputStream is=connect.download(filename, leaderIP);
									FileOutputStream fos = new FileOutputStream(file);
									int inByte;
									while((inByte = is.read()) != -1)
									     fos.write(inByte);
									is.close();
									fos.close();	
								} 
								JOptionPane.showMessageDialog(null, "save succeed");
							
							}
						}catch (Exception e1) {
							e1.printStackTrace();
						}

					}
				}
			}
		});
		btnRename.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if(searchOrNot) {//in search state
					List indexList=getSelectedIndex(searchedData);
					if(indexList.size()==0 || indexList.size()>1) {
						JOptionPane.showMessageDialog(null, "Please select one file to rename","Notice", JOptionPane.ERROR_MESSAGE);
					}else {
						String inputValue = JOptionPane.showInputDialog("Please input a new name");
						if(inputValue==null) {
							
						}else if(!inputValue.equals("")) {
							String originalFilename=(String) searchedData.get((int)indexList.get(0)).get(1);
							
							//****TO DO*****
							//transfer originalFilename and inputValue to server
							String result=connect.rename(originalFilename, inputValue, leaderIP);
							if(result.contentEquals("fail")) {
								JOptionPane.showMessageDialog(null, "Server broken down","Notice", JOptionPane.ERROR_MESSAGE);
							}else if(result.equals("error")) {
								JOptionPane.showMessageDialog(null, "Rename fails","Notice", JOptionPane.ERROR_MESSAGE);
							}else if(result.equals("success")) {
								searchedData.get((int)indexList.get(0)).setElementAt(inputValue,1);
								searchedData.get((int)indexList.get(0)).setElementAt(getTime(),3);
								initTable(searchedData);
								//update data
//								for(int i=0;i<data.size();i++) {
//									if(data.get(i).get(1).equals(originalFilename)) {
//										data.get(i).setElementAt(inputValue,1);
//										
//									}
//								}
								initData();
//								initTable(data);
							}
						}else {
							JOptionPane.showMessageDialog(null, "Please input a valid name","Notice", JOptionPane.ERROR_MESSAGE);
						}
					}
				}else {
					List indexList=getSelectedIndex(data);
					if(indexList.size()==0 || indexList.size()>1) {
						JOptionPane.showMessageDialog(null, "Please select one file to rename","Notice", JOptionPane.ERROR_MESSAGE);
					}else {
						String inputValue = JOptionPane.showInputDialog("Please input a new name");
						if(inputValue==null) {
							
						}else if(!inputValue.equals("")) {
							String originalFilename=(String) data.get((int)indexList.get(0)).get(1);
//							data.get((int)indexList.get(0)).setElementAt(inputValue,1);
//							data.get((int)indexList.get(0)).setElementAt(getTime(),3);
//							initTable(data);
							//****TO DO*****
							//transfer originalFilename and inputValue to server
							String result=connect.rename(originalFilename, inputValue, leaderIP);
							if(result.contentEquals("fail")) {
								JOptionPane.showMessageDialog(null, "Server broken down","Notice", JOptionPane.ERROR_MESSAGE);
							}else if(result.equals("error")) {
								JOptionPane.showMessageDialog(null, "Rename fails","Notice", JOptionPane.ERROR_MESSAGE);
							}else if(result.equals("success")) {
								initData();
								initTable(data);
							}
						}else {
							JOptionPane.showMessageDialog(null, "Please input a valid name","Notice", JOptionPane.ERROR_MESSAGE);
						}
					}
				
				}
			}
		});
		btnDelete.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if(searchOrNot) {//in search state
					List indexList=getSelectedIndex(searchedData);
					
					if(indexList.size()>0) {
						List<String> filenameList=new ArrayList<String>();
						for(int i=0;i<indexList.size();i++) {
							String filename=(String) searchedData.get((int)indexList.get(i)).get(1);
							String result=connect.delete(filename, leaderIP);
							if(result.contentEquals("fail")) {
								JOptionPane.showMessageDialog(null, "Server broken down","Notice", JOptionPane.ERROR_MESSAGE);
							}else if(result.equals("error")) {
								JOptionPane.showMessageDialog(null, "Delete fails","Notice", JOptionPane.ERROR_MESSAGE);
							}else if(result.equals("success")) {
								searchedData.remove((int)indexList.get(i)-i);
							}

						}
						initTable(searchedData);
						initData();
						//****TO DO*****
						//transfer filenameList to delete to server
						
					}else {
						JOptionPane.showMessageDialog(null, "Please select at least one file to delete","Notice", JOptionPane.ERROR_MESSAGE);
					}
				}else {
					List indexList=getSelectedIndex(data);
					if(indexList.size()>0) {
						List<String> filenameList=new ArrayList<String>();
						for(int i=0;i<indexList.size();i++) {
							String filename=(String) data.get((int)indexList.get(i)).get(1);
							//filenameList.add(filename);
							//data.remove((int)indexList.get(i)-i);	
							String result=connect.delete(filename, leaderIP);
							if(result.contentEquals("fail")) {
								JOptionPane.showMessageDialog(null, "Server broken down","Notice", JOptionPane.ERROR_MESSAGE);
							}else if(result.equals("error")) {
								JOptionPane.showMessageDialog(null, "Delete fails","Notice", JOptionPane.ERROR_MESSAGE);
							}else if(result.equals("success")) {
//								initData();
							}

						}
						initData();
						initTable(data);
						//****TO DO*****
						//transfer filenameList to delete to server
					
					}else {
						JOptionPane.showMessageDialog(null, "Please select at least one file to delete","Notice", JOptionPane.ERROR_MESSAGE);
					}
				}
			}
		});
		btnShare.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if(searchOrNot) {//in search state
					List indexList=getSelectedIndex(searchedData);
					
					if(indexList.size()>=1) {
						List<String> filenameList=new ArrayList<String>();
						for(int i=0;i<indexList.size();i++) {
							filenameList.add((String) searchedData.get((int)indexList.get(i)).get(1));	
						}
						String inputValue = JOptionPane.showInputDialog("Please input the name of the person you want to share with");
						//****TO DO*****
						//transfer filenameList and inputValue to server
						if(inputValue==null) {
							
						}else {
							String flag="";
							for(String filename:filenameList) {
								flag=connect.share(inputValue, filename, leaderIP);
								if(flag.equals("not exists")) {
									JOptionPane.showMessageDialog(null, "Target user does not exist", "Notice", JOptionPane.ERROR_MESSAGE);
									break;
								}else if(flag.equals("error")) {
									JOptionPane.showMessageDialog(null, "Error", "Notice", JOptionPane.ERROR_MESSAGE);	
									break;
								}
							}
							if(flag.equals("success")) {
								JOptionPane.showMessageDialog(null, "File shared successfully");	
							}else if(flag.equals("fail")) {
								JOptionPane.showMessageDialog(null, "Server broken down","Notice", JOptionPane.ERROR_MESSAGE);
							}
						
						}
					}else {
						JOptionPane.showMessageDialog(null, "Please select at least one file to share","Notice", JOptionPane.ERROR_MESSAGE);
					}
				}else {
					List indexList=getSelectedIndex(data);
					
					if(indexList.size()>=1) {
						List<String> filenameList=new ArrayList<String>();
						for(int i=0;i<indexList.size();i++) {
							filenameList.add((String) data.get((int)indexList.get(i)).get(1));	
						}
						String inputValue = JOptionPane.showInputDialog("Please input the name of the person you want to share with");
						//****TO DO*****
						//transfer filenameList and inputValue to server
						if(inputValue==null) {
							
						}else {
							String flag="";
							for(String filename:filenameList) {
								flag=connect.share(inputValue, filename, leaderIP);
								if(flag.equals("not exists")) {
									JOptionPane.showMessageDialog(null, "Target user does not exist", "Notice", JOptionPane.ERROR_MESSAGE);
									break;
								}else if(flag.equals("error")) {
									JOptionPane.showMessageDialog(null, "Error", "Notice", JOptionPane.ERROR_MESSAGE);	
									break;
								}
							}
							if(flag.equals("success")) {
								JOptionPane.showMessageDialog(null, "File shared successfully");	
							}else if(flag.equals("fail")) {
								JOptionPane.showMessageDialog(null, "Server broken down","Notice", JOptionPane.ERROR_MESSAGE);
							}
						
						}
					}else {
						JOptionPane.showMessageDialog(null, "Please select at least one file to share","Notice", JOptionPane.ERROR_MESSAGE);
					}
				
				}
			}
		});
		btnSearch.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				if(btnSearch.getText().equals("Search")) {
					if(textField.getText()=="")
						textField.setText("Please input the file to search.");
					else
					{
						searchedData=new Vector();
						String input = textField.getText();
						for(int i=0;i<data.size();i++) {
							String filename=(String)data.get(i).get(1);
							if(filename.indexOf(input)!=-1) {
								searchedData.add(data.get(i));
							}
						}
						initTable(searchedData);
						btnSearch.setText("Cancel");
					}	
					searchOrNot=true;
				}else {
					textField.setText("");
					initTable(data);
					btnSearch.setText("Search");
					searchOrNot=false;
				}
			}
		});

		Timer t=new Timer();
		t.schedule(new TimerTask(){
			   @Override
			   public void run(){
				   /*...Your task...*/
				   leaderIP=connect.getLeader();
				   lblNewLabel.setText("Server: "+leaderIP);
				   ArrayList<List> receive=connect.receive(leaderIP);
				   if (receive.size()==0) {
					   
				   }else {
					   String user=(String)receive.get(0).get(0);
					   String file=(String)receive.get(0).get(1);
					   int temp;
					   if(receive.size()==1) {
						   temp=JOptionPane.showConfirmDialog(null, user+" shares file '"+file+"' with you. Do you want to accept?","Notice", JOptionPane.YES_NO_OPTION);
					   }else {
						   temp=JOptionPane.showConfirmDialog(null, user+" shares files '"+file+"' ,etc. with you. Do you want to accept?","Notice", JOptionPane.YES_NO_OPTION);
					   }
					   if(temp==JOptionPane.YES_OPTION) {
						   for(int i=0;i<receive.size();i++) {
							   String result=connect.acceptShare((String)receive.get(i).get(0), (String)receive.get(i).get(1), leaderIP);
							   if(result.contentEquals("fail")) {
									JOptionPane.showMessageDialog(null, "Server broken down","Notice", JOptionPane.ERROR_MESSAGE);
								}else if(result.equals("error")) {
									JOptionPane.showMessageDialog(null, "Accept fails","Notice", JOptionPane.ERROR_MESSAGE);
								}else if(result.equals("success")) {
								}
						   }
						   initData();
						   if(searchOrNot==false) { 
							   initTable(data);
						   }else {
							   textField.setText("");
							   initTable(data);
							   searchOrNot=false;
							   btnSearch.setText("Search");
						   }
					   }else {
						   for(int i=0;i<receive.size();i++) {
							   String result=connect.declineShare((String)receive.get(i).get(0), (String)receive.get(i).get(1), leaderIP);
							   if(result.contentEquals("fail")) {
									JOptionPane.showMessageDialog(null, "Server broken down","Notice", JOptionPane.ERROR_MESSAGE);
								}else if(result.equals("error")) {
									JOptionPane.showMessageDialog(null, "Decline fails","Notice", JOptionPane.ERROR_MESSAGE);
								}else if(result.equals("success")) {
								}
						   }
					   }
				   }
				   }
			}, 1000,1000);

		
//		MaterialUIMovement.add (btnUpload, MaterialColors.GRAY_100);
//		MaterialUIMovement.add (btnDownload, MaterialColors.GRAY_100);
//		MaterialUIMovement.add (btnDelete, MaterialColors.GRAY_100);
//		MaterialUIMovement.add (btnRename, MaterialColors.GRAY_100);
//		MaterialUIMovement.add (btnShare, MaterialColors.GRAY_100);

		frame.pack ();
		frame.setVisible (true);
		frame.setDefaultCloseOperation(frame.EXIT_ON_CLOSE);
	}
	public void setFileChooserFont(Component[] comp)
	  {
	    for(int x = 0; x < comp.length; x++)
	    {
	      if(comp[x] instanceof Container) setFileChooserFont(((Container)comp[x]).getComponents());
	      try{comp[x].setFont(font);}
	      catch(Exception e){}//do nothing
	    }
	  }
	
	private void initTable(Vector<Vector> data){
		Vector headerNames=new Vector();
		headerNames.add("");
		headerNames.add("file name");
		headerNames.add("size");
		headerNames.add("modified time");
		//this.initData();
		tableModel=new checkTable(data,headerNames);
		table.setModel(tableModel);
		table.getTableHeader().setDefaultRenderer(new checkHeader(table));
	}
	
	private void initData() {
		//*****TO DO*****
		//initiate the original data of the user
		//get the data from server
		data=new Vector();
		connect.init(data,leaderIP);
		
	}
//	private void addData(String fileName,String size,String time) {
//		Vector newVector=new Vector();
//		newVector.add(false);
//		newVector.add(fileName);
//		newVector.add(size);
//		newVector.add(time);
//		data.add(newVector);
//	}
	private List getSelectedIndex(Vector<Vector>data) {
		List indexList=new ArrayList<>();
		for(int i=0;i<data.size();i++) {
			if(data.get(i).get(0).equals(true)) {
				indexList.add(i);
				
			}
		}
		return indexList;
	}
	private String getFileSize(File file) {
		long length=file.length();
		String filesize;
		if(length<(long)1000) {
			filesize=String.valueOf(length);
			return (String)filesize+" B";
		}else if(length<(long)1000000) {
			filesize=String.valueOf(String.format("%.3f",length/1000.0));
			return filesize+" KB";
		}else {
			filesize=String.valueOf(String.format("%.3f",length/1000000.0));
			return filesize+" MB";
		}
	}
	private String getTime() {
		SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");  
		return (String)df.format(System.currentTimeMillis());
	}
	

}
