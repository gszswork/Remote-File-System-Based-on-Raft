package client;

import javax.swing.JCheckBox;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableCellRenderer;

import java.awt.Component;
import java.awt.event.*;

import javax.swing.*;

public class checkHeader implements TableCellRenderer {
	checkTable tableModel;
	JTableHeader tableHeader;
	final JCheckBox selectBox;
	public checkHeader(JTable table) {
		this.tableModel = (checkTable)table.getModel();
		this.tableHeader = table.getTableHeader();
		selectBox = new JCheckBox(tableModel.getColumnName(0));
		selectBox.setSelected(false);
		tableHeader.addMouseListener(new MouseAdapter() {
			public void mouseClicked(MouseEvent e) {
				if (e.getClickCount() > 0) {
					int selectColumn = tableHeader.columnAtPoint(e.getPoint());
					if (selectColumn == 0) {
						boolean value = !selectBox.isSelected();
						selectBox.setSelected(value);
						tableModel.selectAllOrNull(value);
						tableHeader.repaint();
						}
				}
			}
			});
		}

	@Override
	public Component getTableCellRendererComponent(JTable table, Object value,boolean isSelected, boolean hasFocus, int row, int column) {
		String valueStr = (String) value;
		JLabel label = new JLabel(valueStr);
		label.setHorizontalAlignment(SwingConstants.CENTER); // 表头标签剧中
		selectBox.setHorizontalAlignment(SwingConstants.CENTER);// 表头标签剧中
		selectBox.setBorderPainted(true);
		JComponent component = (column == 0) ? selectBox : label;
		component.setForeground(tableHeader.getForeground());
		component.setBackground(tableHeader.getBackground());
		component.setFont(tableHeader.getFont());
		component.setBorder(UIManager.getBorder("TableHeader.cellBorder"));
		return component;
		}
		
}
