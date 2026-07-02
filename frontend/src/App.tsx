import "./App.css";

function App() {
  //if I treat this as the home page the very first thing I need is two buttons to take me to the workoutlog or enter the dungeon
  // right now the dungeon is unavailable so the only working button will be the workout log button
  return (
    <main>
      <h1>Workout Dungeon</h1>
      <button type="button">Workout Log</button>
      <button type="button" disabled>
        Enter the Dungeon (Coming Soon)
      </button>
    </main>
  );
}

export default App;
