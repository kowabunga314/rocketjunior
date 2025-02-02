import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Tree from '../components/Tree';

const mockData = [
  {
    id: 1,
    name: "Rocket",
    path: "/Rocket",
    properties: { Mass: "12000.000", Height: "18.000" },
    descendants: [
      {
        id: 2,
        name: "Stage1",
        path: "/Rocket/Stage1",
        properties: {},
        descendants: [
          {
            id: 4,
            name: "Engine1",
            path: "/Rocket/Stage1/Engine1",
            properties: { ISP: "12.156", Thrust: "9.493" },
            descendants: [],
          },
          {
            id: 5,
            name: "Engine2",
            path: "/Rocket/Stage1/Engine2",
            properties: { ISP: "11.632", Thrust: "9.413" },
            descendants: [],
          },
          {
            id: 6,
            name: "Engine3",
            path: "/Rocket/Stage1/Engine3",
            properties: { ISP: "12.551", Thrust: "9.899" },
            descendants: [],
          },
        ],
      },
      {
        id: 7,
        name: "Stage2",
        path: "/Rocket/Stage2",
        properties: {},
        descendants: [
          {
            id: 8,
            name: "Engine4",  // Call this Engine4 to simplify lookups
            path: "/Rocket/Stage2/Engine4",
            properties: { ISP: "15.110", Thrust: "1.622" },
            descendants: [],
          }
        ]
      }
    ],
  },
];

const enterPathQuery = async (path = '/Rocket', waitText = '▼ Rocket') => {
  const inputElement = screen.getByPlaceholderText('Enter node path (i.e. Rocket, Rocket/Stage1)');
  fireEvent.change(inputElement, { target: { value: path } });

  await waitFor(() => {
    expect(screen.getByText(waitText)).toBeInTheDocument();
  });
};

test('toggles collapsed state of nodes', async () => {
  render(<Tree data={mockData} />);

  // Populate the input element
  await enterPathQuery();
  
  const rocketNode = screen.getByText('▼ Rocket');
  
  // Initially, descendants should not be hidden
  expect(screen.getByText(/Stage1$/)).toBeInTheDocument();
  expect(screen.getAllByText(/Engine1$/)[0]).toBeInTheDocument();
  expect(screen.getByText(/Engine2$/)).toBeInTheDocument();
  expect(screen.getByText(/Engine3$/)).toBeInTheDocument();
  expect(screen.getByText(/Stage2$/)).toBeInTheDocument();
  expect(screen.getAllByText(/Engine1$/)[1]).toBeInTheDocument();
  
  // Click to collapse the Rocket node
  fireEvent.click(rocketNode);
  expect(screen.getByText('▶ Rocket')).toBeInTheDocument();
  
  // After collapsing Rocket, Stage1 should not be visible
  expect(screen.queryByText(/Stage1$/)).toBeNull();
  // After collapsing Rocket, Stage1 engines should not be visible
  expect(screen.queryByText(/Engine1$/)).toBeNull();
  expect(screen.queryByText(/Engine2$/)).toBeNull();
  expect(screen.queryByText(/Engine3$/)).toBeNull();
  // Stage2 and its engine should also not be visible
  expect(screen.queryByText(/Stage2$/)).toBeNull();
  expect(screen.queryByText(/Engine1$/)).toBeNull();
  
  // Click to expand the Rocket node
  fireEvent.click(rocketNode);
  expect(screen.getByText('▼ Rocket')).toBeInTheDocument();
  
  // After expanding Rocket, Stage1 should be visible
  expect(screen.getByText('▼ Stage1')).toBeInTheDocument();
  // After expanding Rocket, Engine1 should be visible
  expect(screen.getAllByText(/Engine1$/)[0]).toBeInTheDocument();
  
  // Click to collapse the Stage1 node
  const stage1Node = screen.getByText('▼ Stage1');
  fireEvent.click(stage1Node);
  expect(screen.getByText('▶ Stage1')).toBeInTheDocument();
  
  // Skip checking Engine1, there is still one under Stage2 and we check for that next
  // Now Engine2 should no longer be visible
  expect(screen.queryByText(/Engine2$/)).toBeNull();
  // Now Engine3 should no longer be visible
  expect(screen.queryByText(/Engine3$/)).toBeNull();
  // Stage2 and its engine should still be visible
  expect(screen.getByText(/Stage2$/)).toBeInTheDocument();
  expect(screen.getByText(/Engine1$/)).toBeInTheDocument(); // Fails if more than 1 returned
  
  // Click to expand Stage1
  fireEvent.click(stage1Node);
  expect(screen.getByText('▼ Stage1')).toBeInTheDocument();
  expect(screen.getAllByText(/Engine1$/)[0]).toBeInTheDocument();
  expect(screen.getByText(/Engine2$/)).toBeInTheDocument();
  expect(screen.getByText(/Engine3$/)).toBeInTheDocument();
  
  // Click to collapse Rocket
  fireEvent.click(rocketNode);
  expect(screen.getByText('▶ Rocket')).toBeInTheDocument();
});

test('renders properties correctly with proper styling', async () => {
  render(<Tree data={mockData} />);

  // Populate the input element
  await enterPathQuery();

  // Find the node for "Stage1"
  const stage1Node = screen.getByText(/Stage1$/);
  expect(stage1Node).toBeInTheDocument();

  // Get all elements matching "ISP" and filter by closest ancestor
  const ispElements = screen.getAllByText(/ISP:/);
  const thrustElements = screen.getAllByText(/Thrust:/);

  // Ensure at least one "ISP" and "Thrust" exists
  expect(ispElements.length).toBeGreaterThan(0);
  expect(thrustElements.length).toBeGreaterThan(0);

  // Check if ISP value greater than 10 is green
  const ispValue = screen.getByText(/12.156/);
  expect(ispValue).toHaveStyle('color: green');

  // Check if Thrust value less than 10 is NOT green
  const thrustValue = screen.getByText(/9.493/);
  expect(thrustValue).not.toHaveStyle('color: green');
});

test('input gets correct data', async () => {
  render(<Tree data={mockData} />);

  // Search for Stage1
  await enterPathQuery('/Rocket/Stage1', '▼ Stage1');

  // Find the node for Stage1
  expect(screen.getByText(/Stage1$/)).toBeInTheDocument();
  // Ensure that Rocket node is not present
  expect(screen.queryByText(/Rocket$/)).toBeNull();
  // Make sure Stage1 descendants are present
  expect(screen.getByText(/Stage1$/)).toBeInTheDocument();
  expect(screen.getAllByText(/Engine1$/)[0]).toBeInTheDocument();
  expect(screen.getByText(/Engine2$/)).toBeInTheDocument();
  expect(screen.getByText(/Engine3$/)).toBeInTheDocument();
  // Make sure Stage2 is not present
  expect(screen.queryByText(/Stage2$/)).toBeNull();

  // Search for Stage2
  await enterPathQuery('/Rocket/Stage2', '▼ Stage2');

  // Find the node for Stage1
  expect(screen.getByText(/Stage2$/)).toBeInTheDocument();
  // Ensure that Rocket node is not present
  expect(screen.queryByText(/Rocket$/)).toBeNull();
  // Make sure Stage1 descendants are present
  expect(screen.getByText(/Stage2$/)).toBeInTheDocument();
  expect(screen.getByText(/Engine1$/)).toBeInTheDocument();
  // Make sure Stage2 is not present
  expect(screen.queryByText(/Stage1$/)).toBeNull();

  // Click to collapse the Rocket node so that descendant nodes don't trip the next check
  const stage2Node = screen.getByText('▼ Stage2');
  fireEvent.click(stage2Node);
  expect(screen.getByText('▶ Stage2')).toBeInTheDocument();

  // Search for Stage1/Engine1
  await enterPathQuery('/Rocket/Stage1/Engine1', '▼ Engine1');

  // Find the node for Stage1
  expect(screen.getByText(/Engine1$/)).toBeInTheDocument();
  // Ensure that Rocket node is not present
  expect(screen.queryByText(/Rocket$/)).toBeNull();
  expect(screen.queryByText(/Stage1$/)).toBeNull();
  expect(screen.queryByText(/Engine2$/)).toBeNull();
  expect(screen.queryByText(/Engine3$/)).toBeNull();
  expect(screen.queryByText(/Stage2$/)).toBeNull();
});

