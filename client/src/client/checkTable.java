package client;
import java.util.Vector;
import javax.swing.table.DefaultTableModel;

public class checkTable extends DefaultTableModel {
	public checkTable(Vector data, Vector columnNames) {
		super(data, columnNames);
	}


	public Class getColumnClass(int c) {
		return getValueAt(0, c).getClass();
	}
	public void selectAllOrNull(boolean value) {
		for (int i = 0; i < getRowCount(); i++) {
			this.setValueAt(value, i, 0);
		}
	}
		
}
