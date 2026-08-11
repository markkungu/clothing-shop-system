<script setup>
</script>


<template>

  <div class="min-h-screen bg-gray-100">

    <nav class="bg-white shadow">
      <div class="max-w-6xl mx-auto px-6 flex gap-1">
        <router-link to="/dashboard" class="nav-link"
          active-class="nav-active">Dashboard</router-link>
        <router-link to="/inventory" class="nav-link"
          active-class="nav-active">Inventory</router-link>
        <router-link to="/sell" class="nav-link"
          active-class="nav-active">Sell</router-link>
        <router-link to="/reports" class="nav-link"
          active-class="nav-active">Sales &amp; Reports</router-link>
      </div>
    </nav>

    <router-view />

  </div>

</template>


<style scoped>
.nav-link {
  padding: 1rem 1.25rem;
  font-weight: 600;
  color: #4b5563;
  border-bottom: 3px solid transparent;
}
.nav-link:hover {
  color: #111827;
}
.nav-active {
  color: #2563eb;
  border-bottom-color: #2563eb;
}
</style>
